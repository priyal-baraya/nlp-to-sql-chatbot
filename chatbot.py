from flask import Flask, render_template, request
from sqlalchemy import text
from app import write_query, db

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    columns = None
    query = None

    if request.method == "POST":
        question = request.form["question"]

        # Generate SQL
        query_state = {"question": question}
        query_state.update(write_query(query_state))
        query = query_state["query"]

        # Run query and extract data
        with db._engine.connect() as conn:
            result_proxy = conn.execute(text(query))  # ✅ wrap in `text()`
            result = result_proxy.fetchall()
            columns = result_proxy.keys()

    return render_template("index.html", result=result, columns=columns, query=query)

if __name__ == "__main__":
    app.run(debug=True)
