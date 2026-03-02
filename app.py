from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import time

from evaluator import DeepSeekEvaluator

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

API_KEY = "sk-ac079804b0c94bad97eae4eef039d3e8"

evaluator = DeepSeekEvaluator(API_KEY)


# 首页
@app.route("/")
def index():
    return render_template("index.html")


# 单条评估
@app.route("/evaluate", methods=["POST"])
def evaluate():

    source = request.form["source"]
    translation = request.form["translation"]

    result = evaluator.evaluate_translation(source, translation)

    return {"result": result}


# Excel批量评估
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = pd.read_excel(filepath)

    results = []

    for _, row in df.iterrows():
        res = evaluator.evaluate_translation(
            row["source_text"],
            row["translated_text"]
        )
        results.append(res)
        time.sleep(1)

    df["DeepSeek评估"] = results

    output_path = os.path.join(
        OUTPUT_FOLDER,
        "评估结果.xlsx"
    )

    df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)