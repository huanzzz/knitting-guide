# 编织指导工具

这是一个帮助编织者跟踪编织进度的工具。它提供了可视化的编织图解和详细的编织说明，让编织过程更加直观和容易理解。

## 功能特点

- 可视化编织图解
- 详细的编织说明
- 行数计数器
- 当前行高亮显示
- 已完成行的标记
- 响应式设计

## 使用方法

1. 运行 Python 解析器生成数据：
```bash
python knitting_parser.py
```

2. 在浏览器中打开 `knitting_guide.html`

3. 使用 +/- 按钮控制当前行

## 文件说明

- `knitting_guide.html`: 主页面
- `styles.css`: 样式文件
- `stitch_config.js`: 针法配置
- `knitting_parser.py`: 数据解析器
- `knitting_data.json`: 生成的编织数据

## 技术栈

- HTML5
- CSS3
- JavaScript (ES6+)
- Python 3 