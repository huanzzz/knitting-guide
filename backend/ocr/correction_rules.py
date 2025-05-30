# 术语映射
TERM_MAPPING = {
    # 基本术语
    "领窜": "领窝",
    "领员": "领窝",
    "碱了": "减了",
    # 符号映射
    "《": "(",
    "》": ")",
    "［": "【",
    "］": "】",
}

# 需要删除的文本
REMOVE_PATTERNS = [
    r"友情提示.*联系微信.*",
]

# 数字模式
NUMBER_PATTERNS = [
    # 修复漏掉的数字
    (r"重复\s+第\s+(\d+)\s+行一一\((\d+)\)\s*针", r"重复第\1行一一\2(\2)针"),
]

# 括号标准化
BRACKET_PATTERNS = [
    (r"《", "("),
    (r"》", ")"),
    (r"［", "【"),
    (r"］", "】"),
]

# 特定上下文替换
CONTEXT_PATTERNS = [
    # 只在数字序列中将"二"替换为破折号
    (r"(\d+)\s*二\s*(\d+)", r"\1——\2"),
    # 在行号描述中将"二"替换为破折号
    (r"第\s*(\d+)\s*行.*二\s*(\d+)", r"第\1行——\2"),
] 