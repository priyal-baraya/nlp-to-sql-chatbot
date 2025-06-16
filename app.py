from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict, Annotated
import getpass
import os
from dotenv import load_dotenv
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")  # Default MySQL port
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google Gemini API Key: ")

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

system_message = """
Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in their question a
specific number of examples, always limit your query to at most {top_k} results.
Never use SELECT * — only query relevant columns.

Only use the following tables:
{table_info}
"""

user_prompt = "Question: {input}"

query_prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_message), ("user", user_prompt)]
)

class QueryOutput(TypedDict):
    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 200,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

def execute_query(state: State):
    tool = QuerySQLDatabaseTool(db=db)
    return {"result": tool.invoke(state["query"])}

def answer_question(state: State):
    response_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the question and SQL result, answer the question clearly."),
        ("human", "Question: {question}\nResult: {result}")
    ])
    return {
        "answer": llm.invoke(
            response_prompt.invoke(
                {"question": state["question"], "result": state["result"]}
            )
        )
    }

def process_question(question: str) -> dict:
    state: State = {"question": question}
    state.update(write_query(state))
    state.update(execute_query(state))
    state.update(answer_question(state))
    return {
        "query": state["query"],
        "answer": state["answer"].content if hasattr(state["answer"], "content") else state["answer"]
    }



if __name__ == "__main__":
    main()
