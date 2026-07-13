#!/usr/bin/env python3
"""
批量移除A House of JONHOS字样
"""

import os
import re
import sys

def remove_johnhouse_from_file(file_path):
    """从单个文件中移除所有A House of JONHOS字样"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 定义需要替换的模式
        patterns = [
            # 第一种模式：单独的A House of JONHOS<br>
            (r'A House of JONHOS<br>', ''),
            # 第二种模式：— A House of JONHOS
            (r'— A House of JONHOS', ''),
            # 第三种模式：A House of JONHOS —
            (r'A House of JONHOS — ', ''),
            # 第四种模式：带点的A House of JONHOS
            (r'· A House of JONHOS', ''),
            # 第五种模式：A House of JONHOS ·
            (r'A House of JONHOS ·', ''),
            # 第六种模式：A House of JONHOS (前面可能有空格)
            (r'\s*A House of JONHOS', ''),
            # 第七种模式：footer中的完整格式
            (r'<p>A House of JONHOS<br><br>', '<p>'),
            (r'<p>A House of JONHOS<br>', '<p>'),
            # 第八种模式：hero subtitle中的格式
            (r'A House of JONHOS — ', ''),
            # 第九种模式：meta description中的格式
            (r'— A House of JONHOS"', '"'),
        ]

        original_content = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # 修复可能出现的双重标点或多余空格
        content = content.replace('|  ·', '|')
        content = content.replace('| ·', '|')
        content = content.replace(' · ', ' ')
        content = content.replace('  ', ' ')
        content = content.replace('| |', '|')

        # 如果内容有变化才保存
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def main():
    # 需要处理的文件列表
    files_to_process = [
        "D:/jonhos总文件/garastor/dist/products.html",
        "D:/jonhos总文件/garastor/dist/collections.html",
        "D:/jonhos总文件/garastor/dist/boutiques.html",
        "D:/jonhos总文件/garastor/dist/journal.html",
        "D:/jonhos总文件/garastor/dist/contact.html",
        "D:/jonhos总文件/garastor/dist/lookbook.html",
        "D:/jonhos总文件/garastor/dist/dashboard.html"
    ]

    print("🔧 正在批量移除'A House of JONHOS'字样...")
    print("=" * 60)

    processed = 0
    for file_path in files_to_process:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            if remove_johnhouse_from_file(file_path):
                print(f"✅ {filename} - 已修改")
                processed += 1
            else:
                print(f"ℹ️ {filename} - 未找到匹配项或无变化")
        else:
            print(f"❌ {file_path} - 文件不存在")

    print("=" * 60)
    print(f"📊 完成: 成功处理 {processed}/{len(files_to_process)} 个文件")

    # 验证index.html已经修改过
    index_file = "D:/jonhos总文件/garastor/dist/index.html"
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'A House of JONHOS' not in content:
                print("✅ index.html - 已验证无A House of JONHOS字样")
            else:
                print("⚠️ index.html - 仍包含A House of JONHOS字样")

    print("\n🎉 批量修改完成！")

if __name__ == "__main__":
    main()