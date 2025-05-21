from flask import Flask, jsonify, render_template, send_from_directory
import os
import json

# 跨域支持
try:
    from flask_cors import CORS
    cors_available = True
except ImportError:
    cors_available = False

app = Flask(
    __name__,
    static_folder='web/static',         # 老web页面静态资源
    template_folder='web/templates'     # 老web页面模板
)
if cors_available:
    CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# row_counts API
@app.route('/api/row-counts')
def row_counts():
    json_path = os.path.join('data', 'output', 'row_counts.json')
    if not os.path.exists(json_path):
        return jsonify({'error': '数据文件不存在'}), 404
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

# extracted_sizes API
@app.route('/api/extracted-sizes')
def extracted_sizes():
    path = os.path.join('data', 'processed', 'extracted_sizes.txt')
    if not os.path.exists(path):
        return jsonify({'error': 'extracted_sizes.txt 不存在'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    sections = []
    current = {'title': '', 'content': ''}
    for line in content.splitlines():
        if line.startswith('#'):
            if current['title']:
                sections.append(current)
            current = {'title': line.lstrip('#').strip(), 'content': ''}
        else:
            current['content'] += line + '\n'
    if current['title']:
        sections.append(current)
    return jsonify({'sections': sections})

# 图片列表 API
@app.route('/api/images')
def images():
    img_dir = os.path.join('data', 'raw', 'images')
    if not os.path.exists(img_dir):
        return jsonify({'files': []})
    files = [f'/imgs/{name}' for name in sorted(os.listdir(img_dir)) if name.endswith('.png')]
    return jsonify({'files': files})

# 静态图片服务（前端直接访问 /imgs/xxx.png）
@app.route('/imgs/<path:filename>')
def serve_img(filename):
    return send_from_directory(os.path.join('data', 'raw', 'images'), filename)

# 老web页面静态文件服务（如有需要）
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)