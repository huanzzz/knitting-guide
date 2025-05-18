import os
import click
from pdf_to_images import pdf_to_images
from src.ocr.image_to_text import images_to_text
from src.ocr.ocr_post_processor import process_text
from src.parser.size_extractor import SizeExtractor

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
    pdf_to_images(pdf_file)
    
    # 2. OCR识别
    print("正在进行OCR识别...")
    text = images_to_text('imgs')
    
    # 3. 后处理
    print("正在进行后处理...")
    processed_text = process_text(text)
    
    # 4. 尺码提取
    print("正在提取尺码...")
    size_extractor = SizeExtractor()
    final_text = size_extractor.process_knitting_pattern(processed_text)
    
    # 5. 保存结果
    with open('data/processed/all_processed_text.txt', 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print("处理完成！")
    print("处理后的文本保存在: data/processed/all_processed_text.txt")

if __name__ == '__main__':
    cli()