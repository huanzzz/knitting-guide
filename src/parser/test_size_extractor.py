import os
from size_extractor import SizeExtractor
import unittest

def test_size_extractor():
    # 创建测试用例
    test_cases = [
        # 测试用例1：基本格式
        {
            "input": "370 (406 - 442 - 478 - 514 - 586 - 622 - 658)",
            "expected": "406"
        },
        # 测试用例2：带行号的格式
        {
            "input": "第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行和第92 (82 - 100 - 102 - 102 - 102 - 112 - 112) 行各增加一个扣眼",
            "expected": "第78行和第82行各增加一个扣眼"
        },
        # 测试用例3：带其他文本的格式
        {
            "input": "用 3.5mm 环针，起 370 (406 - 442 - 478 - 514 - 586 - 622 - 658)针",
            "expected": "用 3.5mm 环针，起 406针"
        }
    ]
    
    # 创建 SizeExtractor 实例
    extractor = SizeExtractor()
    
    # 运行测试
    for i, test_case in enumerate(test_cases, 1):
        result = extractor.extract_second_size(test_case["input"])
        print(f"测试用例 {i}:")
        print(f"输入: {test_case['input']}")
        print(f"期望输出: {test_case['expected']}")
        print(f"实际输出: {result}")
        print(f"测试{'通过' if result == test_case['expected'] else '失败'}\n")

    # 测试 all_processed_text_corrected.txt 文件
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(workspace_root, 'data', 'processed', 'all_processed_text_corrected.txt')
    print(f"尝试读取文件: {file_path}")  # 添加调试信息
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        processed_content = extractor.process_knitting_pattern(content)
        print("处理 all_processed_text_corrected.txt 文件结果:")
        print(processed_content)
    else:
        print("文件不存在，请检查路径。")

class TestSizeExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = SizeExtractor()
        
    def test_extract_sizes(self):
        test_cases = [
            # 测试用例1：简单的数字在前格式
            {
                "input": "用 3.5mm 环针，起 370 (406 - 442 - 478 - 514 - 586 - 622 - 658)针",
                "expected": "用 3.5mm 环针，起 406针"
            },
            # 测试用例2：文字在前格式
            {
                "input": "第72 (72 - 78 - 84 - 84 - 84 - 92 - 92)行和第92 (82 - 100 - 102 - 102 - 102 - 112 - 112) 行各增加一个扣眼",
                "expected": "第72行和第82 行各增加一个扣眼"
            },
            # 测试用例3：带单位的格式
            {
                "input": "剩51 (56 - 65 - 71 - 81 - 87 - 92)针",
                "expected": "剩56针"
            },
            # 测试用例4：多个括号的格式
            {
                "input": "第20到59 (59 - 63 - 67 - 67 - 67 - 73 - 73)行织平针",
                "expected": "第20到59行织平针"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            with self.subTest(test_case=i):
                result = self.extractor.extract_second_size(test_case["input"])
                self.assertEqual(result, test_case["expected"], 
                               f"测试用例 {i} 失败：\n输入：{test_case['input']}\n期望：{test_case['expected']}\n实际：{result}")

if __name__ == '__main__':
    unittest.main()

if __name__ == "__main__":
    test_size_extractor() 