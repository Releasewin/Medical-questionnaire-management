"""
批量压缩图片脚本

使用方法：
  pip install Pillow
  python compress_images.py <图片文件夹路径>

例如：
  python compress_images.py F:\reader-study-test\images

效果：
  - 原图保留在 images_backup/ 中（自动备份）
  - 压缩后的图片替换原文件
  - 4MB 的图片通常压缩到 100-300KB，视觉质量几乎无损

可调参数（在下方修改）：
  MAX_LONG_SIDE  图片最长边的像素上限，超过会等比缩小
  JPEG_QUALITY   JPEG 压缩质量，1-95，越低文件越小但越模糊
"""

import os
import sys
import shutil
from PIL import Image

# ============ 可调参数 ============
MAX_LONG_SIDE = 1200   # 最长边不超过 1200px（超声图片这个尺寸足够清晰）
JPEG_QUALITY = 85      # JPEG 质量，80 是文件大小和清晰度的平衡点
# ==================================

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

def compress_image(input_path, output_path):
    """压缩单张图片"""
    try:
        img = Image.open(input_path)

        # 如果是 RGBA（带透明通道），转成 RGB（JPEG 不支持透明）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 等比缩小
        w, h = img.size
        long_side = max(w, h)
        if long_side > MAX_LONG_SIDE:
            scale = MAX_LONG_SIDE / long_side
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # 保存为 JPEG
        img.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        return True
    except Exception as e:
        print(f"  ✗ 压缩失败: {input_path} — {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python compress_images.py <图片文件夹路径>")
        print("例如: python compress_images.py F:\\reader-study-test\\images")
        sys.exit(1)

    images_dir = sys.argv[1]
    if not os.path.isdir(images_dir):
        print(f"错误: {images_dir} 不是有效的文件夹")
        sys.exit(1)

    # 创建备份文件夹
    backup_dir = images_dir.rstrip('/\\') + '_backup'
    # if not os.path.exists(backup_dir):
    #     print(f"正在备份原图到 {backup_dir} ...")
    #     shutil.copytree(images_dir, backup_dir)
    #     print("备份完成。")
    # else:
    #     print(f"备份文件夹已存在: {backup_dir}，跳过备份。")

    # 统计
    total = 0
    success = 0
    total_before = 0
    total_after = 0

    # 遍历所有子文件夹
    for root, dirs, files in os.walk(images_dir):
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            total += 1
            filepath = os.path.join(root, f)
            size_before = os.path.getsize(filepath)
            total_before += size_before

            # 输出文件统一用 .jpg 后缀
            out_name = os.path.splitext(f)[0] + '.jpg'
            out_path = os.path.join(root, out_name)

            if compress_image(filepath, out_path):
                # 如果原文件后缀不是 .jpg，删掉原文件
                if filepath != out_path and os.path.exists(filepath):
                    os.remove(filepath)

                size_after = os.path.getsize(out_path)
                total_after += size_after
                ratio = (1 - size_after / size_before) * 100 if size_before > 0 else 0
                success += 1

                # 每 50 张打印一次进度
                if success % 50 == 0:
                    print(f"  已处理 {success} 张...")

    print(f"\n完成！")
    print(f"  处理图片: {success}/{total} 张")
    print(f"  压缩前总大小: {total_before / 1024 / 1024:.1f} MB")
    print(f"  压缩后总大小: {total_after / 1024 / 1024:.1f} MB")
    print(f"  压缩率: {(1 - total_after / total_before) * 100:.1f}%")
    # print(f"\n原图备份在: {backup_dir}")
    # print(f"如果压缩效果满意，可以删除备份文件夹节省空间。")
    print(f"\n注意: 如果原图有 .png/.bmp/.tif 后缀的文件已被转为 .jpg，")
    print(f"请重新运行 generate_manifest.py 更新图片清单。")

if __name__ == '__main__':
    main()
