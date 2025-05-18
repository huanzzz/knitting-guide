from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path, out_dir='imgs', dpi=300):
    os.makedirs(out_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    # 计算需要的补零位数
    total_pages = len(pages)
    padding = len(str(total_pages))
    
    for i, page in enumerate(pages):
        # 使用补零的方式命名，例如：page_001.png, page_002.png
        img_path = os.path.join(out_dir, f'page_{str(i+1).zfill(padding)}.png')
        page.save(img_path, 'PNG')
        image_paths.append(img_path)
    return image_paths

if __name__ == '__main__':
    pdf_to_images('your.pdf')