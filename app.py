
from flask import Flask, render_template, request, jsonify
from analytics import DataLoadError, answer_question, get_analytics

app = Flask(__name__)
MAX_QUESTION_LENGTH = 500


@app.route("/", methods=["GET", "POST"])
def home():
    question = ""
    answer = ""
    error = None

    try:
        metrics = get_analytics()
    except DataLoadError as data_error:
        metrics = None
        error = str(data_error)

    if request.method == "POST":
        question = request.form.get("question", "").strip()[:MAX_QUESTION_LENGTH]

        if not question:
            answer = "Please enter a question."
        elif error:
            answer = "Business data is currently unavailable."
        else:
            answer = answer_question(question, metrics)

    return render_template(
        "index.html",
        metrics=metrics,
        question=question,
        answer=answer,
        error=error,
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "BI-Ajent backend is running"
    })

@app.route("/api/analytics", methods=["GET"])
def analytics_api():
    try:
        metrics = get_analytics()
    except DataLoadError as data_error:
        return jsonify({
            "status": "error",
            "error": {"code": "DATA_SOURCE_UNAVAILABLE", "message": str(data_error)},
        }), 503

    return jsonify({
        "status": "success",
        "data": metrics
    })

if __name__ == "__main__":
    app.run(debug=True)