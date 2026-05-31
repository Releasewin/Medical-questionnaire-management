"""
生成 image-manifest.json 的脚本

使用方法：
  python generate_manifest.py /path/to/images

这个脚本会扫描指定文件夹下的所有 caseN/ 子文件夹，
收集每个子文件夹里的图片文件名（jpg/jpeg/png/bmp/tif/tiff），
按文件名排序后输出到同目录的 image-manifest.json 文件。

例如你的图片文件夹结构是：
  reader_study_images/
    case1/
      img001.jpg
      img002.jpg
    case2/
      img001.jpg
    ...

运行：
  python generate_manifest.py reader_study_images

会在 reader_study_images/ 文件夹里生成 image-manifest.json，内容类似：
  {
    "case1": ["img001.jpg", "img002.jpg"],
    "case2": ["img001.jpg"],
    ...
  }
"""

import os
import sys
import json
import re

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif', '.webp'}

def generate_manifest(images_dir):
    manifest = {}
    
    # 找到所有 caseN 文件夹
    entries = os.listdir(images_dir)
    case_dirs = [d for d in entries if re.match(r'^case\d+$', d) and os.path.isdir(os.path.join(images_dir, d))]
    
    # 按数字排序
    case_dirs.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    for case_dir in case_dirs:
        case_path = os.path.join(images_dir, case_dir)
        files = os.listdir(case_path)
        
        # 只保留图片文件
        images = [f for f in files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
        
        # 按文件名自然排序
        images.sort(key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', x)])
        
        if images:
            manifest[case_dir] = images
    
    return manifest

def main():
    if len(sys.argv) < 2:
        print("用法: python generate_manifest.py <图片文件夹路径>")
        print("例如: python generate_manifest.py ./images")
        sys.exit(1)
    
    images_dir = sys.argv[1]
    
    if not os.path.isdir(images_dir):
        print(f"错误: {images_dir} 不是一个有效的文件夹路径")
        sys.exit(1)
    
    manifest = generate_manifest(images_dir)
    
    # 输出到图片文件夹所在的目录
    output_path = os.path.join(images_dir, '..', 'image-manifest.json')
    # 如果 images_dir 就是项目根目录下的 images/，那就输出到项目根目录
    output_path = os.path.normpath(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    total_images = sum(len(v) for v in manifest.values())
    print(f"完成！扫描到 {len(manifest)} 个 case，共 {total_images} 张图片")
    print(f"清单文件保存到：{output_path}")

if __name__ == '__main__':
    main()
