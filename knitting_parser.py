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
        prompt = f"""
        请解析以下编织图解，并以JSON格式输出结果。JSON应包含以下信息：
        - 总行数
        - 每行的总针数
        - 每针的编号和对应的针法
        - 每行的原始编织说明文本
        
        编织图解：
        {pattern_text}
        
        请以以下JSON格式输出（不要包含任何markdown代码块标记，如```json或```）：
        {{
            "total_rows": 整数,
            "pattern": [
                {{
                    "row_number": 行号,
                    "stitches_per_row": 该行的总针数,
                    "stitches": [
                        {{
                            "stitch_number": 针号,
                            "stitch_type": "针法类型"
                        }}
                    ],
                    "instruction": "该行的原始编织说明文本"
                }}
            ]
        }}
        
        注意：
        1. 输出必须是有效的JSON格式，不能有任何多余的文字或代码块标记。
        2. 对于重复的针法（如"1下针，1上针，重复到结束"），需要展开为具体的每一针。
        3. 如果没有明确每行的针数，则使用起针数作为每行针数。
        4. stitches数组必须包含该行所有针的详细信息。
        5. instruction字段需要包含该行的完整原始编织说明文本，包括所有相关的说明和换行。
        6. 只输出一份JSON，不要重复，不要有多余内容。
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "你是一个专业的编织图解解析器，请将编织图解转换为结构化的JSON数据。对于重复的针法，需要展开为具体的每一针。例如，如果一行是'1下针，1上针，重复到结束（共20针）'，那么stitches数组应该包含20个元素，交替显示下针和上针。同时，请保持每行编织说明的原始格式，包括所有相关的说明和换行。"},
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
    起18针
    第 1 行： 上针
第 2 行：下针
第 3 行：上针
第 4 行：【左上2并1，空加针】到最后1针，1下
第 5 和 7 行：上针
第 6 行：下针。
    """
    
    # 创建编织数据对象
    knitting_data = parser.create_knitting_data(title, pattern_text)
    
    # 保存到文件
    knitting_data.save_to_file('knitting_data.json')
    
    # 打印结果
    print(json.dumps(knitting_data.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 