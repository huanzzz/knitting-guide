import os
import sys
import json

# 直接从根目录导入
from knitting_parser import KnittingPatternParser

def test_parser():
    # 创建解析器实例
    parser = KnittingPatternParser()
    
    # 构建输入和输出文件的完整路径
    input_file = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'extracted_sizes.txt')
    output_file = os.path.join(os.path.dirname(__file__), 'data', 'output', 'parsed_result.json')
    
    print(f"正在读取文件: {input_file}")
    
    # 读取测试文件
    with open(input_file, 'r', encoding='utf-8') as f:
        pattern_text = f.read()
    
    print("文件读取成功，开始解析...")
    
    # 解析编织图解
    result = parser.parse_pattern(pattern_text)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 将结果保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"解析结果已保存到: {output_file}")
    
    # 打印完整结果
    print("\n完整解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 打印统计信息
    print(f"\n总行数: {result.get('total_rows', 0)}")
    print("\n各部分信息:")
    for section in result.get('sections', []):
        print(f"\n{section.get('section_title')}:")
        print(f"  行数: {len(section.get('rows', []))}")

if __name__ == "__main__":
    test_parser() 