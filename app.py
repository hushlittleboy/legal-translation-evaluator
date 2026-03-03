from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import time
from openai import OpenAI

# =====================
# Flask App
# =====================

app = Flask(__name__)

# =====================
# DeepSeek API 初始化（安全版）
# =====================

API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = None

if API_KEY:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.deepseek.com"
    )

# =====================
# DeepSeek Evaluator
# =====================

def evaluate_translation(source_text, translated_text):

    if not client:
        return "错误：未配置 DEEPSEEK_API_KEY"

    prompt = f"""
你是一名法律翻译专家，请从以下方面评估法律翻译：

- 准确性
- 流畅性
- 风格一致性
- 术语准确与一致
- 逻辑结构完整再现
- 文化概念处理

源文本：{source_text}

译文：{translated_text}

评分规则：
Critical 扣25分
Major 扣10分
Minor 扣1分

输出格式必须严格如下：

最终得分：[分数]/100
错误评析：
- [Critical/Major/Minor]>错误类型>译文错误片段

示例1： 
源文本：民事主体从事民事活动，不得违反法律，不得违背公序良俗。 
译文：The parties to civil legal relations shall not conduct civil activities in violation of the law, nor contrary to public order and good morals. 
输出结果： 最终得分：90/100
-Major>语法错误> conduct 是动词，nor contrary 是形容词，语法错误。 

示例2： 源文本：研究开发人取得专利权的，委托人可以依法实施该专利。 
译文：Where the developer is granted a patent, the commissioning party may exploit such patent gratuitously. 
输出结果： 最终得分：90/100 
-Major>错译-用词错误> gratuitously 意为自愿地，免费地，源文本中为“依法”， 语义偏差，翻译错误
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        timeout=240
    )

    return response.choices[0].message.content.strip()

# =====================
# 首页
# =====================

@app.route("/")
def index():
    return render_template("index.html")

# =====================
# 单条评估
# =====================

@app.route("/evaluate", methods=["POST"])
def evaluate():

    source = request.form.get("source")
    translation = request.form.get("translation")

    if not source or not translation:
        return jsonify({"result": "请输入完整文本"})

    try:
        result = evaluate_translation(source, translation)
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"result": f"评估失败：{str(e)}"})

# =====================
# Excel 批量评估
# =====================

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")

    if not file:
        return "未上传文件"

    df = pd.read_excel(file)

    results = []

    for _, row in df.iterrows():

        try:
            response = evaluate_translation(
                row["source_text"],
                row["translated_text"]
            )

        except Exception as e:
            response = f"ERROR: {str(e)}"

        results.append(response)

        time.sleep(1)

    df["DeepSeek评估"] = results

    output_path = "evaluation_result.xlsx"
    df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

# =====================
# Railway 启动入口
# =====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
