import os
from knitting_parser import KnittingPatternParser
import json

def test_parser_with_extracted_sizes():
    # 初始化解析器
    parser = KnittingPatternParser()
    
    # 读取文件
    input_file = os.path.join('..', '..', 'data', 'processed', 'all_processed_text_corrected.txt')
    print(f"\n正在读取文件: {os.path.abspath(input_file)}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 第一步：使用 SizeExtractor 提取尺码
    print("\n第一步：使用 SizeExtractor 提取尺码...")
    extracted_content = parser.size_extractor.process_knitting_pattern(content)
    print("尺码提取完成！")
    
    # 保存提取后的内容
    extracted_file = os.path.join('..', '..', 'data', 'processed', 'extracted_sizes.txt')
    with open(extracted_file, 'w', encoding='utf-8') as f:
        f.write(extracted_content)
    print(f"提取后的内容已保存到: {os.path.abspath(extracted_file)}")
    
    # 第二步：使用 KnittingPatternParser 解析内容
    print("\n第二步：使用 KnittingPatternParser 解析内容...")
    result = parser.parse_pattern(extracted_content)
    
    # 保存解析结果
    output_file = os.path.join('..', '..', 'data', 'output', 'parsed_pattern.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n解析结果已保存到: {os.path.abspath(output_file)}")
    
    # 打印解析结果统计
    print("\n解析结果统计：")
    print(f"总行数: {result.get('total_rows', 0)}")
    print(f"模式数组长度: {len(result.get('pattern', []))}")
    
    # 打印完整的解析结果
    print("\n完整的解析结果：")
    for i, item in enumerate(result.get('pattern', []), 1):
        print(f"\n{i}. {json.dumps(item, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    test_parser_with_extracted_sizes() 