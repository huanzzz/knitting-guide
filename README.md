# Knitting Pattern Processing System

This is a complete system for processing knitting patterns, including OCR recognition, text processing, and parsing functions.

## Directory Structure

```
.
├── src/                    # Source code directory
│   ├── ocr/               # OCR related code
│   │   ├── image_to_text.py
│   │   ├── ocr_post_processor.py
│   │   ├── correction_rules.py
│   │   └── badcase_cli.py
│   ├── parser/            # Parser related code
│   │   ├── knitting_parser.py
│   │   └── text_to_json.py
│   ├── web/               # Web interface related code
│   │   ├── knitting_guide.html
│   │   ├── styles.css
│   │   └── stitch_config.js
│   └── utils/             # Utility functions
│       └── config.py
├── data/                  # Data directory
│   ├── raw/              # Raw data
│   │   ├── PDF/
│   │   ├── imgs/
│   │   ├── pattern.png
│   │   └── badcases.json
│   ├── processed/        # Processed data
│   │   ├── all_processed_text.txt
│   │   └── processed_page_*.png.txt
│   └── output/           # Output data
│       ├── result.json
│       └── knitting_data.json
├── versions/             # Version management
│   └── v1/              # Version 1
│       ├── knitting_parser.py
│       └── README.md
├── docs/                 # Documentation
├── requirements.txt      # Project dependencies
└── README.md            # Project description
```

## Main Features

1. OCR Processing
   - PDF to image conversion
   - Image text recognition
   - Text post-processing
   - Error correction

2. Text Parsing
   - Knitting pattern parsing
   - Stitch pattern recognition
   - Data structuring

3. Web Interface
   - Knitting guide display
   - Stitch configuration
   - Style customization

## Usage

1. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. OCR Processing
   ```bash
   python src/ocr/image_to_text.py
   ```

3. Text Parsing
   ```bash
   python src/parser/knitting_parser.py
   ```

## Version Management

- Use `versions` directory to manage different code versions
- Each version has independent documentation and instructions
- Can maintain multiple versions simultaneously

## Notes

- Need to set OPENAI_API_KEY environment variable
- Ensure correct data directory structure
- Recommend using virtual environment

---

# 编织图解处理系统

这是一个用于处理编织图解的完整系统，包括OCR识别、文本处理和解析等功能。

## 目录结构

```
.
├── src/                    # 源代码目录
│   ├── ocr/               # OCR相关代码
│   │   ├── image_to_text.py
│   │   ├── ocr_post_processor.py
│   │   ├── correction_rules.py
│   │   └── badcase_cli.py
│   ├── parser/            # 解析相关代码
│   │   ├── knitting_parser.py
│   │   └── text_to_json.py
│   ├── web/               # Web界面相关代码
│   │   ├── knitting_guide.html
│   │   ├── styles.css
│   │   └── stitch_config.js
│   └── utils/             # 工具函数
│       └── config.py
├── data/                  # 数据目录
│   ├── raw/              # 原始数据
│   │   ├── PDF/
│   │   ├── imgs/
│   │   ├── pattern.png
│   │   └── badcases.json
│   ├── processed/        # 处理后的数据
│   │   ├── all_processed_text.txt
│   │   └── processed_page_*.png.txt
│   └── output/           # 输出数据
│       ├── result.json
│       └── knitting_data.json
├── versions/             # 版本管理
│   └── v1/              # 版本1
│       ├── knitting_parser.py
│       └── README.md
├── docs/                 # 文档
├── requirements.txt      # 项目依赖
└── README.md            # 项目说明
```

## 主要功能

1. OCR处理
   - PDF转图片
   - 图片文字识别
   - 文本后处理
   - 错误修正

2. 文本解析
   - 编织图解解析
   - 针法识别
   - 数据结构化

3. Web界面
   - 编织指南展示
   - 针法配置
   - 样式定制

## 使用方法

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. OCR处理
   ```bash
   python src/ocr/image_to_text.py
   ```

3. 文本解析
   ```bash
   python src/parser/knitting_parser.py
   ```

## 版本管理

- 使用 `versions` 目录管理不同版本的代码
- 每个版本都有独立的文档和说明
- 可以同时维护多个版本

## 注意事项

- 需要设置 OPENAI_API_KEY 环境变量
- 确保数据目录结构正确
- 建议使用虚拟环境 