import openai
import json
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RowCounter:
    def __init__(self):
        """初始化计数器，使用环境变量中的API密钥"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("未找到 OPENAI_API_KEY 环境变量")
        print(f"API密钥前6位: {api_key[:6]}...")
        self.client = openai.OpenAI(api_key=api_key)

    def split_pattern_by_sections(self, pattern_text: str) -> List[Dict[str, str]]:
        """按#标记切分编织内容，支持全角#"""
        sections = []
        current_section = {"title": "", "content": ""}

        for line in pattern_text.split('\n'):
            line = line.lstrip()
            if line.startswith('#') or line.startswith('＃'):
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

        return sections

    def count_section_rows(self, section: Dict[str, str]) -> Dict[str, Any]:
        """使用AI统计单个部分的行数（优化提示词）"""
        print(f"\n统计部分: {section['title']}")
        
        # 优化后的提示词
        prompt = f"""请分析以下编织图解的【{section['title']}】部分，只统计本区间内容中明确出现的所有行号。注意：

1. 只统计本区间（即本段落）出现的行号，不要统计其它区间的行号。
2. 处理所有行号表达式，包括：
   - 第X行
   - 第X和Y行
   - 第X到Y行（必须展开为连续的行号，如"第9到20行"应展开为[9,10,11,...,20]）
   - 第X-Y行（同上，必须展开为连续的行号）
   - 重复第X到Y行再N次（必须展开为所有重复的行号，如"重复第40到59行再1次"应展开为[40,41,...,59]）
   - 第X到Y行的所有奇数/偶数行（必须展开为所有符合条件的行号）
3. 对于区间表达式（如"第X到Y行"），必须展开为连续的行号列表，不要只记录起始和结束行号。
4. 对于"重复"指令，要正确计算重复后的行号，并且每个行号只统计一次。
5. 对于"所有奇数/偶数行"的表达式，必须展开为所有符合条件的行号。
6. 不要推测或补全未在本区间出现的行号。
7. 不要统计针数，x针代表一行要织的针数，而不是行数。
8. 返回JSON字符串，格式如下（注意rows为升序、无重复的行号列表）：
{{
    "row_count": 总行数,
    "start_row": 起始行号,
    "end_row": 结束行号,
    "rows": [所有行号的升序列表]
}}
9. 如果区间内没有有效行号，row_count为0，start_row和end_row为null。

示例：
如果内容包含"第1到3行"和"第5行"，应该返回：
{{
    "row_count": 4,
    "start_row": 1,
    "end_row": 5,
    "rows": [1, 2, 3, 5]
}}

如果内容包含"第9到20行"，应该返回：
{{
    "row_count": 12,
    "start_row": 9,
    "end_row": 20,
    "rows": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
}}

如果内容包含"第11-18行的所有奇数行"，应该返回：
{{
    "row_count": 4,
    "start_row": 11,
    "end_row": 17,
    "rows": [11, 13, 15, 17]
}}

如果内容包含"重复第40到59行再1次"，应该返回：
{{
    "row_count": 20,
    "start_row": 40,
    "end_row": 59,
    "rows": [40, 41, 42, ..., 59]
}}

【{section['title']}】部分内容如下：
{section['content']}"""

        try:
            # 调用AI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的编织图解分析助手，擅长准确统计行号。你必须返回一个有效的JSON字符串。对于区间表达式和重复指令，必须展开为连续的行号列表。不要统计针数，x针代表一行要织的针数，而不是行数。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # 打印AI返回的原始内容
            print(f"AI返回内容: {response.choices[0].message.content}")
            
            # 解析AI返回的JSON
            result = json.loads(response.choices[0].message.content)
            
            # 使用起始行和结束行计算总行数
            if result["start_row"] is not None and result["end_row"] is not None:
                result["row_count"] = result["end_row"] - result["start_row"] + 1
            
            return {
                "section_title": section['title'],
                "row_count": result["row_count"],
                "start_row": result["start_row"],
                "end_row": result["end_row"]
            }
            
        except Exception as e:
            print(f"AI统计出错: {str(e)}")
            print(f"AI返回内容: {response.choices[0].message.content if 'response' in locals() else '无返回'}")
            return {
                "section_title": section['title'],
                "row_count": 0,
                "start_row": None,
                "end_row": None
            }

    def count_pattern_rows(self, pattern_text: str) -> Dict[str, Any]:
        """统计编织图解的行数"""
        print("\n开始统计编织图解行数...")
        
        # 按部分切分内容
        sections = self.split_pattern_by_sections(pattern_text)
        
        # 统计每个部分的行数
        section_counts = []
        for section in sections:
            section_count = self.count_section_rows(section)
            section_counts.append(section_count)
        
        # 合并所有部分的结果
        result = {
            "sections": section_counts,
            "total_rows": sum(section.get('row_count', 0) for section in section_counts)
        }
        
        return result

def compare_results(actual: Dict[str, Any], expected: Dict[str, Any]) -> None:
    """比较实际结果和预期结果"""
    print("\n比对结果:")
    print("-" * 50)
    
    # 创建预期结果的查找字典
    expected_sections = {section["section_title"]: section for section in expected["sections"]}
    
    # 比较每个部分
    for section in actual["sections"]:
        title = section["section_title"]
        if title in expected_sections:
            expected_section = expected_sections[title]
            print(f"\n{title}:")
            
            # 比较行数
            actual_count = section["row_count"]
            expected_count = expected_section["row_count"]
            if actual_count != expected_count:
                print(f"  行数不匹配: 实际={actual_count}, 预期={expected_count}")
            else:
                print(f"  行数匹配: {actual_count}")
            
            # 比较起始行
            actual_start = section["start_row"]
            expected_start = expected_section["start_row"]
            if actual_start != expected_start:
                print(f"  起始行不匹配: 实际={actual_start}, 预期={expected_start}")
            
            # 比较结束行
            actual_end = section["end_row"]
            expected_end = expected_section["end_row"]
            if actual_end != expected_end:
                print(f"  结束行不匹配: 实际={actual_end}, 预期={expected_end}")
        else:
            print(f"\n{title}: 在预期结果中未找到")
    
    # 比较总行数
    actual_total = actual["total_rows"]
    expected_total = expected["total_rows"]
    print("\n总行数比较:")
    if actual_total != expected_total:
        print(f"总行数不匹配: 实际={actual_total}, 预期={expected_total}")
    else:
        print(f"总行数匹配: {actual_total}")
    
    print("-" * 50)

def main():
    counter = RowCounter()
    
    # 读取输入文件
    input_file = '../data/processed/extracted_sizes.txt'
    with open(input_file, 'r', encoding='utf-8') as f:
        pattern_text = f.read()
    
    # 统计行数
    result = counter.count_pattern_rows(pattern_text)
    
    # 打印结果
    print("\n统计结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 保存结果到文件
    output_file = '../data/output/row_counts.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    
    # 读取预期结果
    expected_file = '../data/processed/expected_row_counts.json'
    with open(expected_file, 'r', encoding='utf-8') as f:
        expected_result = json.load(f)
    
    # 比较结果
    compare_results(result, expected_result)

if __name__ == "__main__":
    main() 