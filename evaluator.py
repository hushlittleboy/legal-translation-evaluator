import time
from openai import OpenAI

class DeepSeekEvaluator:

    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def evaluate_translation(self, source_text, translated_text):

        prompt = f"""
你是一名法律翻译专家，有着丰厚的法律翻译经验，请你从专业译者的角度，从准确性、流畅性、风格一致性、术语准确与一致、逻辑结构完整再现、文化概念恰当处理的方面，评估下列法律文本的翻译。 
任务：评估法律翻译质量，给出翻译质量得分（满分100 分），并指出翻译的错误之处、错误类型及严重程度。 
输入参数： 
源语：中文 
目标语：英文 
源文本：{source_text} 
译文：{translated_text} 
错误分级标准： 
- Critical：导致法律效力改变（义务主体错译等） 
- Major：引发歧义影响司法适用（逻辑关系偏差等） 
- Minor：有错误但不影响理解（冗余修饰、语言不正式等） 
输出要求：
 计算翻译质量得分（满分100 分）：每个Critical 错误扣25 分，每个 Major 错误扣10 分，每个Minor 错误扣1 分（起始分100 分，扣分后不低于0 分）。 
 最后，严格按指定输出格式，只呈现结果。 
 输出格式： 
 最终得分：[分数]/100 
 错误评析： - [Critical/Major/Minor] >[错误类型] >[译文错误片段] （注：错误类型需按严重程度降序排列）
 示例1： 源文本：民事主体从事民事活动，不得违反法律，不得违背公序良俗。 
 译文：The parties to civil legal relations shall not conduct civil activities in violation of the law, nor contrary to public order and good morals. 
 输出结果： 最终得分：90/100 
 -Major>语法错误> conduct 是动词，nor contrary 是形容词，语法错误。 
 示例2： 源文本：研究开发人取得专利权的，委托人可以依法实施该专利。 
 译文：Where the developer is granted a patent, the commissioning party may exploit such patent gratuitously. 
 输出结果： 最终得分：90/100 
 -Major>错译-用词错误> gratuitously 意为自愿地，免费地，源文本中为“依法”， 语义偏差，翻译错误
"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        return response.choices[0].message.content.strip()