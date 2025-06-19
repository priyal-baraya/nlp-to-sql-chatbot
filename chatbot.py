from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from app import process_question, db, engine
from sqlalchemy.sql import text

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if "chat_history" not in session:
        session["chat_history"] = []

    query = answer = result = columns = None

    if request.method == 'POST':
        question = request.form['question']
        chat_history = session["chat_history"]

        try:
            response = process_question(question, chat_history)
            query = response['query']
            answer = response['answer']

            with engine.connect() as conn:
                result_proxy = conn.execute(text(query))
                result = result_proxy.fetchall()
                columns = result_proxy.keys()

            chat_history.append({
                "question": question,
                "answer": answer,
                "query": query,
                "result": result,
                "columns": columns
            })

            session["chat_history"] = chat_history
            session.modified = True

        except Exception as e:
            answer = f"Error: {str(e)}"
            query = "SQL generation failed."

    return render_template('index.html', query=query, answer=answer, result=result, columns=columns, chat_history=session["chat_history"])


@app.route('/clear', methods=['POST'])
def clear():
    session.pop("chat_history", None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
