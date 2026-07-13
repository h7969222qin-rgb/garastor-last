#!/usr/bin/env python3
"""
GARASTOR Content Generator
从现有JSON数据 + JS数据结构生成:
1. content/products/ 下 21 个产品 MD 文件
2. content/journal/ 下 6 个期刊 MD 文件
3. 自动扫描 images/products/ 目录获取实际图片数量
"""

import json
import os
import glob
import re

BASE = r"D:\jonhos总文件\garastor\dist"
CONTENT = os.path.join(BASE, "content")
PRODUCTS_DIR = os.path.join(CONTENT, "products")
JOURNAL_DIR = os.path.join(CONTENT, "journal")
IMAGES_DIR = os.path.join(BASE, "images", "products")

# ══════════════════════════════════════════════
# Data: from js/product-pages.js enriched descriptions
# ══════════════════════════════════════════════
PRODUCT_RICH_DATA = {
    "strip-plank": {
        "Budelli": {
            "description": "Subtle earthy tones that ground a room without overwhelming it. The essence of quiet luxury.",
            "features": ["Solid Oak", "Matte Finish", "180mm Width", "European Origin"],
        },
        "Burano": {
            "description": "Warm caramel hues that bring organic warmth to modern interiors.",
            "features": ["Solid Oak", "Natural Finish", "180mm Width", "Low-VOC"],
        },
        "Capri": {
            "description": "Aged patina that tells a story. For those who appreciate character.",
            "features": ["Reclaimed Oak", "Hand-Scraped", "Variable Width", "Antique Finish"],
        },
        "Elba": {
            "description": "Soft mossy greens that connect indoor spaces with outdoor serenity.",
            "features": ["European Oak", "Oil Finish", "200mm Width", "Sustainable"],
        },
        "Levanzo": {
            "description": "Morning light captured in wood. A fresh start for any space.",
            "features": ["White Oak", "Natural Oil", "180mm Width", "FSC Certified"],
        },
        "Lschia": {
            "description": "Twilight hues for sophisticated, moody interiors.",
            "features": ["Dark Oak", "Matte Finish", "210mm Width", "Water-Resistant"],
        },
        "Murano": {
            "description": "Named after the famous glass island - precision and clarity in form.",
            "features": ["Smoked Oak", "High-Gloss", "150mm Width", "Made in Italy"],
        },
        "Palmarola": {
            "description": "Distant mountain grays for a serene, elevated feel.",
            "features": ["Ash Wood", "Wire-Brushed", "190mm Width", "Long Length"],
        },
        "Sicily": {
            "description": "Pure, clean whites inspired by Sicilian moonlight.",
            "features": ["White Ash", "Chalk Finish", "200mm Width", "Bleached Effect"],
        },
    },
    "chevron": {
        "Capraia": {
            "description": "Dynamic angles that create visual movement and architectural interest.",
            "features": ["European Oak", "Chevron Pattern", "45° Angle", "Precision Fit"],
        },
        "Giannutri": {
            "description": "Heritage pattern with modern execution for timeless elegance.",
            "features": ["Solid Oak", "Herringbone", "Traditional", "Oil Finish"],
        },
        "Lipari": {
            "description": "Volcanic island inspiration - bold, dramatic, unforgettable.",
            "features": ["Dark Walnut", "Chevron", "Matte", "Wide Plank"],
        },
        "Nisida": {
            "description": "Coastal hues that bring the Mediterranean indoors.",
            "features": ["White Oak", "Weathered Finish", "Chevron", "Beach Tone"],
        },
        "Pianosa": {
            "description": "Flat island simplicity - clean lines, perfect symmetry.",
            "features": ["Ash Wood", "Horizontal Chevron", "Natural", "Smooth Surface"],
        },
        "Salina": {
            "description": "Salty air and sea spray captured in wood grain.",
            "features": ["Reclaimed Oak", "Salvaged", "Vintage Chevron", "Distressed"],
        },
    },
    "herringbone": {
        "Comacina": {
            "description": "Classic herringbone reimagined for contemporary luxury.",
            "features": ["European Oak", "Traditional Pattern", "Oil Finish", "20mm Thick"],
        },
        "Elba": {
            "description": "Island-inspired herringbone with natural, textured finish.",
            "features": ["Solid Oak", "Herringbone", "Natural Oil", "Sustainable"],
        },
        "Gorgona": {
            "description": "Wild, untamed beauty in structured herringbone form.",
            "features": ["Reclaimed Wood", "Rustic Herringbone", "Wire-Brushed", "Character Grade"],
        },
        "Lsola-Madre": {
            "description": "Mother island - the foundation of our herringbone collection.",
            "features": ["Premium Oak", "Fine Herringbone", "Hand-Finished", "Luxe Grade"],
            "chineseNameOverride": "马德雷",
            "codeOverride": "Lsola Madre 马德雷",
        },
        "Zannone": {
            "description": "Imported excellence - rare woods in precise herringbone.",
            "features": ["Imported Oak", "Luxury Herringbone", "Custom Length", "Installation Service"],
        },
        "Salina": {
            "description": "Salt-affected wood for unique coastal character.",
            "features": ["Salt-Treated Oak", "Coastal Herringbone", "Weathered", "Marine Grade"],
        },
    },
}

# ══════════════════════════════════════════════
# Family display names & descriptions
# ══════════════════════════════════════════════
FAMILY_INFO = {
    "strip-plank": {
        "name": "Strip Plank",
        "chineseName": "条板",
        "eyebrow": "The Purist",
        "description": "The quiet luxury of restraint. Long lines, expanded space. Less, perfected.",
        "stats": "9 styles",
    },
    "chevron": {
        "name": "Chevron",
        "chineseName": "鱼骨拼",
        "eyebrow": "The Statement",
        "description": "Bold angles that command the room. For spaces that deserve to be unforgettable.",
        "stats": "6 styles",
    },
    "herringbone": {
        "name": "Herringbone",
        "chineseName": "人字拼",
        "eyebrow": "The Classic",
        "description": "Parquetry reimagined as olfactory art. A silent symphony of wood and light.",
        "stats": "6 styles",
    },
}


def scan_product_images():
    """扫描 images/products/ 目录，获取每个产品的实际图片列表"""
    result = {}
    for family in ["strip-plank", "chevron", "herringbone"]:
        result[family] = {}
        family_dir = os.path.join(IMAGES_DIR, family)
        if not os.path.isdir(family_dir):
            continue
        for product_name in os.listdir(family_dir):
            product_dir = os.path.join(family_dir, product_name)
            if not os.path.isdir(product_dir):
                continue
            images = sorted(
                [f for f in os.listdir(product_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            )
            result[family][product_name] = {
                "count": len(images),
                "images": images,
                "has_panorama": any("panorama" in img.lower() for img in images),
            }
    return result


def generate_product_md(product, family, code, chinese_name, rich_data, images_info):
    """生成单个产品 MD 文件"""
    image_base_path = f"images/products/{family}/{product}"

    # 封面图
    cover = f"/images/products/{family}/{product}/1.jpg"
    if images_info and "panorama" in images_info:
        # 有 panorama.jpg 的产品用特殊封面
        pass

    # 规格/描述
    desc = rich_data.get("description", "") if rich_data else ""
    features = rich_data.get("features", []) if rich_data else []

    # 如果有 override 的中文名和code
    chinese_name_override = rich_data.get("chineseNameOverride", "") if rich_data else ""
    code_override = rich_data.get("codeOverride", "") if rich_data else ""

    if code_override:
        code = code_override
    if chinese_name_override:
        chinese_name = chinese_name_override

    image_count = images_info["count"] if images_info else 5

    # 生成图片路径模板
    # 检查实际图片文件名模式
    if images_info:
        regular_images = [img for img in images_info["images"] if "panorama" not in img.lower()]
        panorama_images = [img for img in images_info["images"] if "panorama" in img.lower()]
    else:
        regular_images = []
        panorama_images = []

    md = f"""---
# GARASTOR Product: {code}
family: {family}
id: {product.lower().replace(' ', '-')}
name: {product}
chineseName: {chinese_name}
code: "{code}"
cover: {cover}
imageCount: {image_count}
imagePath: {image_base_path}/{{n}}.jpg
"""
    if images_info and images_info["has_panorama"]:
        md += f"hasPanorama: true\n"
        md += f"panoramaPath: {image_base_path}/panorama.jpg\n"

    md += f"""status: active
published: true
description: >
  {desc}
features:
"""
    for feat in features:
        md += f"  - \"{feat}\"\n"

    md += f"""familyInfo:
  name: "{FAMILY_INFO[family]['name']}"
  chineseName: "{FAMILY_INFO[family]['chineseName']}"
  eyebrow: "{FAMILY_INFO[family]['eyebrow']}"
---

# {code}

{desc}

**Collection:** {FAMILY_INFO[family]['name']} ({FAMILY_INFO[family]['chineseName']}) — {FAMILY_INFO[family]['eyebrow']}

**Features:**
"""
    for feat in features:
        md += f"- {feat}\n"

    md += f"""
**Gallery:** {image_count} high-resolution product images available.
"""
    if images_info and images_info["has_panorama"]:
        md += f"\n> This product includes a panorama view image.\n"

    return md


def generate_journal_md(article):
    """生成单篇期刊 MD 文件"""
    slug = article.get("slug", "")

    # 从 journal.html 提取的描述和更多内容
    display_date = article.get("displayDate", article.get("date", ""))
    excerpt = article.get("excerpt", "")
    content_body = article.get("content", "")
    read_time = article.get("readTime", "5 min read")
    author = article.get("author", "GARASTOR Editorial")
    tag_cn = article.get("chineseTag", "")
    title_cn = article.get("chineseTitle", "")
    image = article.get("image", "")

    md = f"""---
title: "{article.get('title', '')}"
chineseTitle: "{title_cn}"
date: {article.get('date', '')}
displayDate: "{display_date}"
slug: {slug}
tag: "{article.get('tag', '')}"
chineseTag: "{tag_cn}"
image: {image}
status: {article.get('status', 'published')}
published: true
author: "{author}"
readTime: "{read_time}"
excerpt: >
  {excerpt}
---

# {article.get('title', '')}

*{tag_cn} · {display_date} · {read_time}*

{excerpt}

---

{content_body}

---

**Author:** {author}
**Published:** {display_date}
"""
    return md


def main():
    print("=" * 60)
    print("GARASTOR Content Generator")
    print("=" * 60)

    # 创建目录
    os.makedirs(PRODUCTS_DIR, exist_ok=True)
    os.makedirs(JOURNAL_DIR, exist_ok=True)

    # 扫描图片
    print("\n[1/4] Scanning product images...")
    images = scan_product_images()

    total_products = sum(len(v) for v in images.values())
    print(f"  Found {total_products} products with images across {len(images)} families")
    for family, products in images.items():
        print(f"    {family}: {len(products)} products")
        for prod, info in products.items():
            extra = " + panorama" if info["has_panorama"] else ""
            print(f"      {prod}: {info['count']} images{extra}")

    # 加载 products.json
    print("\n[2/4] Loading product data from JSON...")
    with open(os.path.join(BASE, "data", "products.json"), "r", encoding="utf-8") as f:
        products_json = json.load(f)

    # 加载 journal.json
    print("\n[3/4] Loading journal data from JSON...")
    with open(os.path.join(BASE, "data", "journal.json"), "r", encoding="utf-8") as f:
        journal_json = json.load(f)

    # 生成产品 MD
    print("\n[4/4] Generating markdown files...")
    product_count = 0
    for family in ["strip-plank", "chevron", "herringbone"]:
        family_data = products_json.get("products", {}).get(family, {})
        items = family_data.get("items", [])

        for item in items:
            prod_id = item.get("id", "")
            prod_name = item.get("name", "")
            code = item.get("code", prod_name)
            chinese_name = item.get("chineseName", "")
            rich = PRODUCT_RICH_DATA.get(family, {}).get(prod_name, {})
            img_info = images.get(family, {}).get(prod_name, None)

            md_content = generate_product_md(
                prod_name, family, code, chinese_name, rich, img_info
            )

            filename = f"{prod_id}.md"
            filepath = os.path.join(PRODUCTS_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)

            product_count += 1
            print(f"  OK content/products/{filename}")

    # 生成期刊 MD
    journal_count = 0
    articles = journal_json.get("articles", [])
    for article in articles:
        slug = article.get("slug", "")
        md_content = generate_journal_md(article)

        filename = f"{slug}.md"
        filepath = os.path.join(JOURNAL_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        journal_count += 1
        print(f"  OK content/journal/{filename}")

    print(f"\n{'=' * 60}")
    print(f"Generated {product_count} product files + {journal_count} journal files")
    print(f"Total: {product_count + journal_count} markdown files")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()