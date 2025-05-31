import openai
import json
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from src.parser.size_extractor import SizeExtractor

# 加载环境变量
load_dotenv()

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
        """初始化解析器，使用环境变量中的API密钥"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("未找到 OPENAI_API_KEY 环境变量")
        self.client = openai.OpenAI(api_key=api_key)
        self.size_extractor = SizeExtractor()

    def split_pattern_by_sections(self, pattern_text: str) -> List[Dict[str, str]]:
        """按#标记切分编织内容"""
        sections = []
        current_section = {"title": "", "content": "", "row_count": 0}
        
        for line in pattern_text.split('\n'):
            if line.strip().startswith('#'):
                if current_section["title"]:  # 如果已经有标题，保存当前部分
                    sections.append(current_section)
                current_section = {
                    "title": line.strip('#').strip(),
                    "content": "",
                    "row_count": 0
                }
            else:
                current_section["content"] += line + '\n'
                # 计算行数
                if "行" in line and ":" in line:
                    current_section["row_count"] += 1
        
        if current_section["title"]:  # 保存最后一部分
            sections.append(current_section)
            
        return sections

    def calculate_row_ranges(self, sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """计算每个部分的行数范围"""
        current_row = 1
        processed_sections = []
        
        for section in sections:
            row_count = section["row_count"]
            if row_count > 0:
                section_data = {
                    "title": section["title"],
                    "content": section["content"],
                    "start_row": current_row,
                    "end_row": current_row + row_count - 1,
                    "row_count": row_count
                }
                current_row += row_count
            else:
                section_data = {
                    "title": section["title"],
                    "content": section["content"],
                    "start_row": current_row,
                    "end_row": current_row,
                    "row_count": 0
                }
            processed_sections.append(section_data)
            
        return processed_sections

    def parse_section(self, section: Dict[str, str], next_section: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """解析单个部分的编织内容"""
        stitch_types = [
            '上针', '下针', '空针', '空加针', '挂针', '加针', '并针', '反针', '绞针', '长针', '引线',
            '左上2并1', '左下二并一', '右上二并一', '右下二并一', 'M1L', 'M1R', 'M1LP', 'M1RP'
        ]
        
        # 准备提示文本
        prompt = f"""
        请解析以下编织图解部分，并以JSON格式输出结果。要求如下：

        1. 前端针法符号配置如下（stitch_type字段必须严格使用下列内容，不要有多余空格、不要用变体、不要用同义词）：
        {stitch_types}

        2. JSON 结构如下：
           {{
             "section_title": "部分标题",
             "rows": [
               {{
                 "type": "row",
                 "row_number": 行号,
                 "stitches_per_row": 针数,
                 "instruction": "该行的原始编织说明文本",
                 "stitch_repeat": [
                   {{
                     "repeat": 重复次数,
                     "stitches": [
                       {{"stitch_type": "针法1"}},
                       {{"stitch_type": "针法2"}},
                       ...
                     ]
                   }}
                 ]
               }},
               {{
                 "type": "meta",
                 "instruction": "非针法类说明"
               }}
             ]
           }}

        3. 对于每一行针法，需要：
           - 准确计算针数
           - 正确识别重复模式
           - 保持原始说明文本
           - 所有stitch_type必须严格从上述列表中选取

        4. 对于非针法类说明，使用meta类型

        当前部分内容：
        {section['content']}

        {'下一部分内容（用于参考针数）：' + next_section['content'] if next_section else ''}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的编织图解解析器，请严格按照要求输出JSON格式的解析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                try:
                    result = json.loads(json_str)
                    result['section_title'] = section['title']
                    return result
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {str(e)}")
                    return {
                        "section_title": section['title'],
                        "rows": []
                    }
            else:
                print("无法在响应中找到有效的JSON")
                return {
                    "section_title": section['title'],
                    "rows": []
                }
                
        except Exception as e:
            print(f"解析错误: {str(e)}")
            return {
                "section_title": section['title'],
                "rows": []
            }

    def parse_pattern(self, pattern_text: str) -> Dict[str, Any]:
        """解析编织图解文本，返回JSON格式的解析结果"""
        # 首先提取第二个尺码的数据
        processed_text = self.size_extractor.process_knitting_pattern(pattern_text)
        
        # 按部分切分内容
        sections = self.split_pattern_by_sections(processed_text)
        
        # 计算每个部分的行数范围
        processed_sections = self.calculate_row_ranges(sections)
        
        # 合并所有部分的结果
        result = {
            "sections": processed_sections,
            "total_rows": sum(section.get('row_count', 0) for section in processed_sections)
        }
        
        return result

    def create_knitting_data(self, title: str, pattern_text: str) -> KnittingData:
        """创建编织数据对象"""
        pattern_json = self.parse_pattern(pattern_text)
        knitting_data = KnittingData(title, pattern_text, pattern_json)
        
        # 确保输出目录存在
        output_dir = os.path.join('data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存到指定目录
        output_file = os.path.join(output_dir, 'knitting_data.json')
        knitting_data.save_to_file(output_file)
        
        return knitting_data

def main():
    parser = KnittingPatternParser()
    
    # 示例编织图解
    title = "背心"
    pattern_text = """
 
衣身
选项一: 朱迪的魔术起针法
用 3. 5mm 环针，起 406针
每根针上 203针 - 221针 - 239针 - 257针 - 293针 - 311针 - 329针
将两根针都放到左手，有活结的棒针现在在前，将背面棒针抽出(针目滑 到环针线上)，工作纱线在右手，织 1行上针，(见"折叠边")


折叠边
第 1行: 上针
第 2行: 下针
第 3行: 上针
第4行:【左上 2 并1，空加针】到最后1针，1 下
第5和7行: 上针
第6行: 下针
第 8行: 将织物对折，正面朝你(反面相对)，工作纱线所在棒针在前，
将两根针上的针目一针对一针织到一起

蕾丝花样
第 9行(反面): 上针
第10行: 3下,【(左上 2 并1) 3次，(空加针，1 下) 5 次，空加针，(右 上2并1) 3次，1上】重复【 】再9次，直至剩 20针，(左上2 并1) 3 次，(空加针，1 下) 5 次，空加针，(右上2 并1) 3次，3 下
第 11-18行的所有奇数行: 20 上,【1 下，17 上】到最后 3针，3 上
第12行(第一个扣眼): 2 下，空加针，右上2并1，16 下，1上,【17 下，1上】到最后 20针，20 下
第14行: 重复 第10行
第16行: 20 下,【1 上，17下】到最后3针，3 下
第 18行: 重复 第 10 行
第 20 到 59 行织平针，同时，每 20 行织扣眼如下
行32 和52(扣眼行): 2下，空加针，右上 2 并1，下针到底

中长款
重复第40到第59行再1次，将在第72行增加一个扣眼; 
第60行: 46下, 收10针，下针到剩56针, 收10针，下针到底
左前片 46 针，后片 91 针，右前片 46 针，后片 91 针，右前片 46 针。


左前片
奇数行织上针
第 61行: 上针
第 62行: 1下， 右上2并1，下针到底一一剩45针
第64到69行: 重复第62行和
第 63行再3次一一剩42针
沿袖笼共织了4-5次减针
第70行: 下针
第72行: 重复第62行一一剩41针
沿袖笼共织了5 5次减针
第74行: 下针

左领窝
第75行: 收20针，上针到底一一21针

第 76行:1下， 右上 2 并1，下针到最后 3针，左上 2 并1，1 下一一19针
奇数行: 上针
第 78行:下针到最后 3针，左上 2 并 1，1 下一一18针
第 80 和84行: 重复 第 76行一一14 针
第 82 和86行: 下针
沿袖笼共减了 8 次，沿领窝减了4次

左后肩
第88行: 下针到最后 3针，左上 2 并1，1 下一一剩13针
沿袖笼减了8次，沿领窝减了5次
奇数行: 上针
第90行: 下针
第 92 行到第 103 行: 重复第 88
行到第91行再3次一一剩10针
沿袖笼共减了8 次，沿领窝减了8次
第 104 行到第 122 行: 平针
收针
    """
    
    # 创建编织数据对象
    knitting_data = parser.create_knitting_data(title, pattern_text)
    
    # 打印结果
    print(json.dumps(knitting_data.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 