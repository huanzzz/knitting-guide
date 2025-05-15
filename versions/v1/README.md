# 编织图解解析器 v1

这是编织图解解析器的第一个版本，专注于基本的针法解析功能。

## 功能特点

1. 基本针法解析
   - 支持常见的针法类型（上针、下针、空针等）
   - 处理重复针法
   - 保持原始编织说明格式

2. 数据结构
   - 使用 JSON 格式存储解析结果
   - 包含针法行和非针法说明
   - 支持保存和加载数据

3. 使用方法
   ```python
   parser = KnittingPatternParser()
   knitting_data = parser.create_knitting_data(title, pattern_text)
   knitting_data.save_to_file('knitting_data.json')
   ```

## 依赖

- Python 3.6+
- openai
- python-dotenv

## 注意事项

- 需要设置 OPENAI_API_KEY 环境变量
- 针法类型必须严格匹配预定义列表
- 建议使用 GPT-4 模型以获得最佳效果 