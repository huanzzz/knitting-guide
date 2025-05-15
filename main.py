import os
import click
from pdf_to_images import convert_pdf_to_images
from image_to_text import images_to_text
from ocr_post_processor import process_file

@click.group()
def cli():
    """编织图解OCR处理工具"""
    pass

@cli.command()
@click.argument('pdf_file', type=click.Path(exists=True))
def process_pdf(pdf_file):
    """处理PDF文件"""
    # 1. 转换PDF为图片
    print("正在转换PDF为图片...")
    convert_pdf_to_images(pdf_file)
    
    # 2. OCR识别
    print("正在进行OCR识别...")
    images_to_text('imgs')
    
    # 3. 后处理
    print("正在进行文本后处理...")
    process_file('all_processed_text.txt', 'all_processed_text_corrected.txt')
    
    print("处理完成！")
    print("原始文本保存在: all_processed_text.txt")
    print("处理后的文本保存在: all_processed_text_corrected.txt")

@cli.command()
def add_badcase():
    """添加新的错误案例"""
    os.system('python3 badcase_cli.py add')

@cli.command()
def list_badcases():
    """列出所有错误案例"""
    os.system('python3 badcase_cli.py list')

if __name__ == '__main__':
    cli()