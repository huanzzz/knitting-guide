import openai
import json
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

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
        print(f"API密钥前6位: {api_key[:6]}...")  # 打印API密钥前6位，确认是否正确加载
        self.client = openai.OpenAI(api_key=api_key)

    def split_pattern_by_sections(self, pattern_text: str) -> List[Dict[str, str]]:
        """按#标记切分编织内容，支持全角#，并打印每一行的内容用于调试"""
        sections = []
        current_section = {"title": "", "content": ""}

        print("开始切分，打印每一行的内容：")
        for line in pattern_text.split('\n'):
            print(f"行内容: {repr(line)}")  # 打印每一行的原始内容
            line = line.lstrip()
            if line.startswith('#') or line.startswith('＃'):
                print(f"找到标题行: {line}")  # 打印找到的标题行
                if current_section["title"]:
                    sections.append(current_section)
                current_section = {
                    "title": line.lstrip('#＃').strip(),
                    "content": ""
                }
            else:
                if current_section["title"]:
                    current_section["content"] += line + '\n'

        if current_section["title"]:
            sections.append(current_section)

        print(f"切分得到 {len(sections)} 个部分")
        for section in sections:
            print(f"部分标题: {section['title']}")
            print(f"内容长度: {len(section['content'])} 字符")

        return sections

    def fill_missing_rows(self, section_content: str, start_row: int, end_row: int) -> List[Dict]:
        """补充缺失的行号"""
        rows = []
        has_odd_rows = "奇数行: 上针" in section_content
        has_even_rows = "偶数行: 下针" in section_content
        
        # 提取现有的行号
        existing_rows = set()
        for line in section_content.split('\n'):
            if '第' in line and '行' in line:
                try:
                    row_num = int(line.split('第')[1].split('行')[0].strip())
                    existing_rows.add(row_num)
                except ValueError:
                    continue
        
        # 补充缺失的行
        for row_num in range(start_row, end_row + 1):
            if row_num not in existing_rows:
                if has_odd_rows and row_num % 2 == 1:
                    rows.append({
                        "type": "row",
                        "row_number": row_num,
                        "instruction": f"第{row_num}行: 上针",
                        "stitch_repeat": [{
                            "repeat": 1,
                            "stitches": [{"stitch_type": "上针"}]
                        }]
                    })
                elif has_even_rows and row_num % 2 == 0:
                    rows.append({
                        "type": "row",
                        "row_number": row_num,
                        "instruction": f"第{row_num}行: 下针",
                        "stitch_repeat": [{
                            "repeat": 1,
                            "stitches": [{"stitch_type": "下针"}]
                        }]
                    })
        
        return rows

    def parse_section(self, section: Dict[str, str], next_section: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """解析单个部分的编织内容"""
        print(f"\n解析部分: {section['title']}")
        print("原始内容:")
        print(section['content'])
        
        # 提取行号范围
        row_numbers = []
        existing_rows = []
        
        for line in section['content'].split('\n'):
            if '第' in line and '行' in line:
                try:
                    # 处理重复指令
                    if '重复' in line and '到' in line:
                        # 提取目标区间
                        target_start = int(line.split('第')[1].split('行')[0].strip())
                        target_end = int(line.split('到第')[1].split('行')[0].strip())
                        
                        # 提取源区间
                        repeat_start = int(line.split('重复第')[1].split('行')[0].strip())
                        repeat_end = int(line.split('到第')[1].split('行')[0].strip())
                        
                        # 计算重复次数
                        repeat_count = 1
                        if '再' in line:
                            repeat_count = int(line.split('再')[1].split('次')[0].strip())
                        
                        # 计算源区间长度
                        source_length = repeat_end - repeat_start + 1
                        # 计算目标区间长度
                        target_length = target_end - target_start + 1
                        
                        # 验证重复次数是否正确
                        if source_length * repeat_count != target_length:
                            print(f"警告：重复次数可能不正确。源区间长度={source_length}，重复次数={repeat_count}，目标区间长度={target_length}")
                            # 调整重复次数
                            repeat_count = target_length // source_length
                        
                        # 生成重复的行
                        for i in range(repeat_count):
                            for j in range(source_length):
                                current_row = target_start + i * source_length + j
                                source_row = repeat_start + j
                                row_numbers.append(current_row)
                                existing_rows.append({
                                    "type": "row",
                                    "row_number": current_row,
                                    "instruction": f"第{current_row}行: 重复第{source_row}行",
                                    "stitch_repeat": [{
                                        "repeat": 1,
                                        "stitches": [{"stitch_type": "下针" if current_row % 2 == 0 else "上针"}]
                                    }]
                                })
                    else:
                        # 处理普通行
                        row_num = int(line.split('第')[1].split('行')[0].strip())
                        row_numbers.append(row_num)
                        existing_rows.append({
                            "type": "row",
                            "row_number": row_num,
                            "instruction": line.strip(),
                            "stitch_repeat": [{
                                "repeat": 1,
                                "stitches": [{"stitch_type": "下针" if row_num % 2 == 0 else "上针"}]
                            }]
                        })
                except ValueError as e:
                    print(f"无法解析行: {line.strip()}, 错误: {str(e)}")
                    continue
        
        if not row_numbers:
            print("未找到任何行号")
            return {
                "section_title": section['title'],
                "rows": []
            }
        
        # 获取行号范围
        start_row = min(row_numbers)
        end_row = max(row_numbers)
        print(f"行号范围: {start_row} - {end_row}")
        
        # 补充缺失的行
        missing_rows = self.fill_missing_rows(section['content'], start_row, end_row)
        print(f"补充了 {len(missing_rows)} 行")
        
        # 合并并排序所有行
        all_rows = existing_rows + missing_rows
        all_rows.sort(key=lambda x: x.get('row_number', float('inf')))
        print(f"总行数: {len(all_rows)}")
        
        return {
            "section_title": section['title'],
            "rows": all_rows
        }

    def parse_pattern(self, pattern_text: str) -> Dict[str, Any]:
        """解析编织图解文本，返回JSON格式的解析结果"""
        print("\n开始解析编织图解...")  # 打印开始解析
        print(f"输入文本长度: {len(pattern_text)} 字符")
        
        # 按部分切分内容
        sections = self.split_pattern_by_sections(pattern_text)
        
        # 解析每个部分
        parsed_sections = []
        for i in range(len(sections)):
            next_section = sections[i + 1] if i + 1 < len(sections) else None
            parsed_section = self.parse_section(sections[i], next_section)
            parsed_sections.append(parsed_section)
        
        # 合并所有部分的结果
        result = {
            "sections": parsed_sections,
            "total_rows": sum(len(section.get('rows', [])) for section in parsed_sections)
        }
        
        print(f"\n解析完成，共 {len(parsed_sections)} 个部分")  # 打印解析完成
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