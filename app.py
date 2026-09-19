from flask import Flask, render_template, request
from analytics import get_analytics, answer_question

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    metrics = get_analytics()

    question = ""
    answer = ""

    if request.method == "POST":
        question = request.form.get("question", "")

        answer = answer_question(question, metrics)

    return render_template(
        "index.html",
        metrics=metrics,
        question=question,
        answer=answer
    )

if __name__ == "__main__":
    app.run(debug=True)