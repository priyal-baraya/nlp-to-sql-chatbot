from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict, Annotated
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database setup
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

# Gemini API setup
if not os.environ.get("GOOGLE_API_KEY"):
    import getpass
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google Gemini API Key: ")

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Prompt templates
system_message = """
You are a helpful data assistant. Given the user question and any prior context, write a syntactically correct SQL query in the {dialect} dialect.
Limit to at most {top_k} results unless otherwise asked. Don't use SELECT * — only include necessary columns.

Database schema:
{table_info}
"""

user_prompt = """Conversation so far:
{history}

Current user question: {input}
"""

query_prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", user_prompt)
])

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    query: Annotated[str, ..., "Syntactically valid SQL query."]

# Chat history (global)
chat_history = []

def write_query(state: State, history_text: str):
    prompt = query_prompt_template.invoke({
        "dialect": db.dialect,
        "top_k": 200,
        "table_info": db.get_table_info(),
        "history": history_text,
        "input": state["question"]
    })
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

def execute_query(state: State):
    tool = QuerySQLDatabaseTool(db=db)
    return {"result": tool.invoke(state["query"])}

def answer_question(state: State, history_text: str):
    response_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Given the user's current question and the SQL result, respond conversationally."),
        ("user", "Conversation so far:\n{history}\n\nCurrent question: {question}\nResult: {result}")
    ])
    return {
        "answer": llm.invoke(response_prompt.invoke({
            "question": state["question"],
            "result": state["result"],
            "history": history_text
        }))
    }

def process_question(question: str, chat_history: list) -> dict:
    state: State = {"question": question}
    history_text = "\n".join([f"User: {msg['question']}\nBot: {msg['answer']}" for msg in chat_history]) if chat_history else ""

    state.update(write_query(state, history_text))
    state.update(execute_query(state))
    state.update(answer_question(state, history_text))

    return {
        "query": state["query"],
        "answer": state["answer"].content if hasattr(state["answer"], "content") else state["answer"]
    }

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = answer = result = columns = None
    if request.method == "POST":
        question = request.form["question"]
        try:
            response = process_question(question, chat_history)
            query = response["query"]
            answer = response["answer"]
            chat_history.append({"question": question, "answer": answer})

            with engine.connect() as conn:
                result_proxy = conn.execute(text(query))
                result = result_proxy.fetchall()
                columns = result_proxy.keys()

        except Exception as e:
            answer = f"Error: {str(e)}"
            query = "SQL generation failed."

    return render_template("index.html", chat_history=[
        {**msg, "query": query if i == len(chat_history)-1 else None, "result": result if i == len(chat_history)-1 else None, "columns": columns if i == len(chat_history)-1 else None}
        for i, msg in enumerate(chat_history)
    ])

@app.route("/clear", methods=["POST"])
def clear():
    global chat_history
    chat_history = []
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
