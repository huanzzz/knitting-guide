import openai
import json
from typing import Dict, List, Any
from config import get_api_key

class KnittingData:
    """编织数据管理类"""
    def __init__(self, title: str = "", pattern_text: str = "", pattern_json: Dict = None):
        self.title = title
        self.pattern_text = pattern_text
        self.pattern_json = pattern_json if pattern_json else {}

    def to_dict(self) -> Dict:
        """将数据转换为字典格式"""
        return {
            "title": self.title,
            "pattern_text": self.pattern_text,
            "pattern_json": self.pattern_json
        }

    def save_to_file(self, filename: str):
        """保存数据到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'KnittingData':
        """从文件加载数据"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(
                title=data.get('title', ''),
                pattern_text=data.get('pattern_text', ''),
                pattern_json=data.get('pattern_json', {})
            )

class KnittingPatternParser:
    def __init__(self):
        """初始化解析器，使用配置中的API密钥"""
        self.client = openai.OpenAI(api_key=get_api_key())

    def parse_pattern(self, pattern_text: str) -> Dict[str, Any]:
        """解析编织图解文本，返回JSON格式的解析结果"""
        stitch_types = [
            '上针', '下针', '空针', '空加针', '挂针', '加针', '并针', '反针', '绞针', '长针', '引线',
            '左上2并1', '左下二并一', '右上二并一', '右下二并一', 'M1L', 'M1R', 'M1LP', 'M1RP'
        ]
        prompt = f"""
        请解析以下编织图解，并以JSON格式输出结果。要求如下：

        1. 前端针法符号配置如下（stitch_type字段必须严格使用下列内容，不要有多余空格、不要用变体、不要用同义词）：
        {stitch_types}

        2. JSON 顶层包含：
           - "total_rows"：仅统计针法行（即 type 为 "row" 的行）的总数
           - "pattern"：数组，顺序与原始 pattern text 完全一致

        3. 对于每一行针法（如"第1行：..."），输出如下结构：
           {{
             "type": "row",
             "row_number": 行号,
             "stitches_per_row": 针数,
             "instruction": "该行的原始编织说明文本"
           }}
           - 如果该行针法是大量重复（如"1下针，1上针，重复到结束，共1000针"），请不要在stitches数组中全部展开，而是用
             "stitch_repeat": [
               {{"repeat": 1, "stitch_type": "下针"}},
               {{"repeat": 1, "stitch_type": "上针"}}
             ]
             来描述循环，并给出stitches_per_row总针数。前端会根据这个字段动态生成所有针的信息。
           - 如果不是大量重复，可以直接输出详细stitches数组。
           - 所有stitch_type字段必须严格从上述列表中选取，不能有任何变体、空格、简繁体、数字变体等。

        4. 对于非针法类说明（如起针、收针、总结、藏线头等），输出如下结构：
           {{
             "type": "meta",
             "instruction": "该说明的原文"
           }}

        5. pattern 数组中的每一项，顺序必须与原始 pattern text 完全一致，不能打乱、不能合并、不能省略。

        6. 只输出一份有效的 JSON，不要有多余内容，不要有 markdown 代码块标记。

        原始编织图解如下：
        {pattern_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "你是一个专业的编织图解解析器，请将编织图解转换为结构化的JSON数据。对于重复的针法，需要展开为具体的每一针。同时，请保持每行编织说明的原始格式，包括所有相关的说明和换行。对于非针法类的说明（如起针、收针、总结等），请将其识别为meta类型，并保持原有顺序。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 从响应中提取JSON字符串
            json_str = response.choices[0].message.content.strip()
            print("API响应内容:", json_str)  # 调试信息
            
            # 尝试解析JSON字符串
            try:
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                print("原始响应内容:", json_str)  # 调试信息
                return None
            
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return None

    def create_knitting_data(self, title: str, pattern_text: str) -> KnittingData:
        """创建编织数据对象"""
        pattern_json = self.parse_pattern(pattern_text)
        return KnittingData(title, pattern_text, pattern_json)

def main():
    parser = KnittingPatternParser()
    
    # 示例编织图解
    title = "折叠边"
    pattern_text = """
    选项一：朱迪的魔术起针法 用 3.5mm 环针，起 406针 = 每根针上203 针，将两根针都放到左手，有活结的棒针现在在前，将背面棒针抽出（针目滑到环针线上），工作纱线在右手，织 1 行上针（见 "折叠边"）。
第1行： 上针
第2行： 下针
第3行： 上针
第4行： 【左上2并1，空加针】到最后1针，1下
第5行和第7行： 上针
第6行： 下针
第8行：将织物对折，正面朝你（反面相对），工作纱线在前，将两根棒针上的针木一对一织到一起
    """
    
    # 创建编织数据对象
    knitting_data = parser.create_knitting_data(title, pattern_text)
    
    # 保存到文件
    knitting_data.save_to_file('knitting_data.json')
    
    # 打印结果
    print(json.dumps(knitting_data.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 