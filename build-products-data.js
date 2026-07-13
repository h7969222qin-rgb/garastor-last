/**
 * GARASTOR products-data.json Builder
 * Reads product data + scans images/ → generates products-data.json
 * Format matches exactly what product-detail.html expects.
 *
 * Usage: node build-products-data.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const IMAGES_DIR = path.join(ROOT, 'images', 'products');

// Product definitions matching product-detail.html expected format
const CATEGORIES = [
  {
    slug: 'strip-plank',
    kilianFamily: 'The Purist',
    nameZh: '条板',
    nameEn: 'Strip Plank',
    description: 'The quiet luxury of restraint. Long lines, expanded space. Less, perfected.',
    products: [
      { code: 'Budelli', name: 'Budelli 布德利', firstImg: 1, images: 5 },
      { code: 'Burano', name: 'Burano 布拉诺', firstImg: 1, images: 5 },
      { code: 'Capri', name: 'Capri 卡普里', firstImg: 1, images: 5 },
      { code: 'Elba', name: 'Elba 厄尔巴', firstImg: 1, images: 5 },
      { code: 'Levanzo', name: 'Levanzo 莱万佐', firstImg: 1, images: 5 },
      { code: 'Lschia', name: 'Lschia 伊斯基亚', firstImg: 1, images: 5 },
      { code: 'Murano', name: 'Murano 穆拉诺', firstImg: 1, images: 5 },
      { code: 'Palmarola', name: 'Palmarola 帕尔马罗拉', firstImg: 1, images: 5 },
      { code: 'Sicily', name: 'Sicily 西西里', firstImg: 1, images: 5 },
    ],
  },
  {
    slug: 'chevron',
    kilianFamily: 'The Statement',
    nameZh: '鱼骨拼',
    nameEn: 'Chevron',
    description: 'Bold angles that command the room. For spaces that deserve to be unforgettable.',
    products: [
      { code: 'Capraia', name: 'Capraia 卡普拉亚', firstImg: 1, images: 5 },
      { code: 'Giannutri', name: 'Giannutri 詹努特里', firstImg: 1, images: 5 },
      { code: 'Lipari', name: 'Lipari 利帕里', firstImg: 1, images: 5 },
      { code: 'Nisida', name: 'Nisida 尼西达', firstImg: 1, images: 5 },
      { code: 'Pianosa', name: 'Pianosa 皮亚诺萨', firstImg: 1, images: 5 },
      { code: 'Salina', name: 'Salina Salina', firstImg: 1, images: 5 },
    ],
  },
  {
    slug: 'herringbone',
    kilianFamily: 'The Classic',
    nameZh: '人字拼',
    nameEn: 'Herringbone',
    description: 'Parquetry reimagined as olfactory art. A silent symphony of wood and light.',
    products: [
      { code: 'Comacina', name: 'Comacina 科马奇纳', firstImg: 1, images: 5 },
      { code: 'Elba', name: 'Elba 埃尔巴', firstImg: 1, images: 5 },
      { code: 'Gorgona', name: 'Gorgona 戈尔戈纳', firstImg: 1, images: 5 },
      { code: 'Lsola-Madre', name: 'Lsola-Madre', firstImg: 1, images: 5 },
      { code: 'Zannone', name: 'Zannone 赞诺内', firstImg: 1, images: 5 },
      { code: 'Salina', name: 'Salina', firstImg: 1, images: 5 },
    ],
  },
];

// ─── Scan actual images to get correct counts ───
function scanImages() {
  const result = {};
  for (const cat of CATEGORIES) {
    result[cat.slug] = {};
    const catDir = path.join(IMAGES_DIR, cat.slug);
    if (!fs.existsSync(catDir)) continue;
    for (const prod of fs.readdirSync(catDir)) {
      const prodDir = path.join(catDir, prod);
      if (!fs.statSync(prodDir).isDirectory()) continue;
      const imgs = fs.readdirSync(prodDir).filter(f => /\.(jpg|jpeg|png|webp)$/i.test(f));
      result[cat.slug][prod] = imgs.length;
    }
  }
  return result;
}

// MAIN
function main() {
  const imgCounts = scanImages();

  // Update image counts from actual filesystem
  for (const cat of CATEGORIES) {
    for (const prod of cat.products) {
      // product-detail.html extracts code up to first space → looks up by that
      const lookupName = prod.code;
      const actual = imgCounts[cat.slug]?.[lookupName];
      if (actual && actual > 0) {
        prod.images = actual;
      }
    }
  }

  const outputPath = path.join(ROOT, 'products-data.json');
  fs.writeFileSync(outputPath, JSON.stringify({ categories: CATEGORIES }, null, 2), 'utf8');

  const total = CATEGORIES.reduce((s, c) => s + c.products.length, 0);
  console.log(`Generated products-data.json: ${CATEGORIES.length} families, ${total} products`);
  for (const cat of CATEGORIES) {
    console.log(`  ${cat.slug}: ${cat.products.length} products`);
  }
}

main();