import openai
import json
from typing import Dict, List, Any
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
        self.client = openai.OpenAI(api_key=api_key)

    def calculate_stitch_count(self, stitch_type: str) -> int:
        """计算单个针法的针数变化"""
        if stitch_type in ['左上2并1', '左下二并一', '右上二并一', '右下二并一']:
            return -1  # 2针并1针，净减1针
        elif stitch_type in ['空加针', '挂针', '加针']:
            return 1   # 加1针
        else:
            return 0   # 普通针法，不改变针数

    def calculate_row_stitches(self, row: Dict) -> int:
        """计算一行的实际针数"""
        if row.get('type') != 'row':
            return 0

        # 获取当前行的针数
        current_stitches = row.get('stitches_per_row')
        if current_stitches is None:
            return 0

        # 如果有重复针法，计算重复针法的针数
        if 'stitch_repeat' in row:
            total_stitches = 0
            for repeat_item in row['stitch_repeat']:
                repeat = repeat_item.get('repeat', 0)
                stitches = repeat_item.get('stitches', [])
                # 计算这个重复项的针数
                for stitch in stitches:
                    stitch_type = stitch.get('stitch_type', '')
                    stitch_change = self.calculate_stitch_count(stitch_type)
                    total_stitches += repeat * stitch_change
            return total_stitches
        
        # 如果是普通针法（如"上针"、"下针"），返回声明的针数
        return current_stitches

    def validate_row_stitches(self, row: Dict, prev_row: Dict = None) -> bool:
        """验证一行的针数是否正确"""
        if row.get('type') != 'row':
            return True

        # 获取当前行的针数
        current_stitches = row.get('stitches_per_row')
        if current_stitches is None:
            return True

        # 计算实际针数
        calculated_stitches = self.calculate_row_stitches(row)
        
        # 如果有上一行，考虑上一行的针数
        if prev_row and prev_row.get('type') == 'row':
            prev_stitches = prev_row.get('stitches_per_row')
            if prev_stitches is not None:
                # 如果是普通针法，直接使用声明的针数
                if 'stitch_repeat' not in row:
                    calculated_stitches = current_stitches
                else:
                    # 如果是重复针法，计算针数变化
                    calculated_stitches = prev_stitches + calculated_stitches

        # 验证计算出的针数是否与声明的一致
        if calculated_stitches != current_stitches:
            print(f"警告：第{row.get('row_number')}行的针数计算不一致")
            print(f"声明针数：{current_stitches}")
            print(f"计算针数：{calculated_stitches}")
            print(f"行内容：{row.get('instruction')}")
            if 'stitch_repeat' in row:
                print(f"重复针法：{json.dumps(row['stitch_repeat'], ensure_ascii=False)}")
            return False

        # 验证重复针法的合理性
        if 'stitch_repeat' in row:
            total_stitches = 0
            for repeat_item in row['stitch_repeat']:
                repeat = repeat_item.get('repeat', 0)
                stitches = repeat_item.get('stitches', [])
                
                # 计算这个重复项的针数
                for stitch in stitches:
                    stitch_type = stitch.get('stitch_type', '')
                    stitch_change = self.calculate_stitch_count(stitch_type)
                    total_stitches += repeat * stitch_change

                # 验证重复次数是否合理
                if len(stitches) > 1:  # 如果是针法序列
                    # 计算每个序列的针数变化
                    sequence_change = sum(self.calculate_stitch_count(s.get('stitch_type', '')) for s in stitches)
                    # 计算合理的重复次数
                    if prev_stitches is not None:
                        expected_repeat = (current_stitches - 1) // abs(sequence_change) if sequence_change != 0 else 0
                        if repeat != expected_repeat:
                            print(f"警告：第{row.get('row_number')}行的重复次数不合理")
                            print(f"当前重复次数：{repeat}")
                            print(f"预期重复次数：{expected_repeat}")
                            print(f"针法序列：{json.dumps(stitches, ensure_ascii=False)}")
                            return False

        return True

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
           - 针数计算规则：
             a. 如果文本中明确说明了针数（如"起203针"），使用该数字
             b. 如果文本中说明了重复模式，需要计算总针数
             c. 如果该行是重复前面的行（如"重复第10行"），使用被重复行的针数
             d. 如果该行是特殊说明（如"上针到底"），使用前一行的针数
           - 如果该行针法是大量重复，使用 stitch_repeat 来描述循环：
             "stitch_repeat": [
               {{
                 "repeat": 重复次数,
                 "stitches": [
                   {{"stitch_type": "针法1"}},
                   {{"stitch_type": "针法2"}},
                   ...
                 ]
               }},
               {{
                 "repeat": 1,
                 "stitches": [
                   {{"stitch_type": "最后的针法"}}
                 ]
               }}
             ]
             注意：
             1. stitches 数组中的针法会作为一个整体重复指定的次数
             2. 每个 stitch_repeat 项都必须包含 stitches 数组，即使是单个针法
             3. 重复次数必须准确计算：
                - 对于【】中的针法序列，需要计算序列的针数变化
                - 根据总针数和序列的针数变化计算重复次数
                - 例如：【左上2并1，空加针】到最后1针，1下
                  * 序列针数变化：-1 + 1 = 0（左上2并1减1针，空加针加1针）
                  * 总针数203，最后1针下针
                  * 重复次数 = (203 - 1) ÷ 2 = 101次
             4. 针数计算必须考虑：
                - 上一行的针数
                - 当前行和上一行的加针、减针、挂针、收针
                - 本行的加针、减针、挂针、收针
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
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个专业的编织图解解析器，请严格按照要求输出JSON格式的解析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            # 提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                
                # 验证每一行的针数
                prev_row = None
                for row in result.get('pattern', []):
                    if not self.validate_row_stitches(row, prev_row):
                        print(f"警告：第{row.get('row_number')}行的针数验证失败")
                    prev_row = row
                
                return result
            else:
                raise ValueError("无法在响应中找到有效的JSON")
        except Exception as e:
            print(f"解析错误: {str(e)}")
            print(f"原始响应内容: {content}")
            return {"pattern_json": {}}

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
    
    # 打印结果
    print(json.dumps(knitting_data.to_dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 