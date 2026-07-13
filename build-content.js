/**
 * GARASTOR Content Build Script
 *
 * Reads content/products/*.md + content/journal/*.md → generates:
 *   data/products.json
 *   data/journal.json
 *
 * Designed for Cloudflare Pages build pipeline:
 *   `npm ci && npm run build`
 *
 * Usage: node build-content.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const CONTENT_DIR = path.join(ROOT, 'content');
const DATA_DIR = path.join(ROOT, 'data');

// ─── Minimal YAML parser (no dependencies needed for simple frontmatter) ───
function parseFrontmatter(content) {
  const lines = content.split(/\r?\n/);
  if (lines[0] !== '---') {
    console.warn('No frontmatter found');
    return { data: {}, body: content };
  }

  const endIdx = lines.indexOf('---', 1);
  if (endIdx === -1) {
    console.warn('Unclosed frontmatter');
    return { data: {}, body: content };
  }

  const fmLines = lines.slice(1, endIdx);
  const body = lines.slice(endIdx + 1).join('\n').trim();
  const raw = fmLines.join('\n');

  // Parse simple YAML frontmatter with nesting support
  // Handles: key: value, key: "value", lists, multiline >/|, nested objects
  const data = {};
  let currentListKey = null;
  let currentList = null;
  let currentMultilineKey = null;
  let currentMultilineLines = [];
  let skipDepth = -1; // when set, skip all lines at indent > skipDepth

  for (let i = 0; i < fmLines.length; i++) {
    const line = fmLines[i];
    const trimmed = line.trim();

    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith('#')) continue;

    const indent = line.length - line.trimStart().length;

    // If we're skipping nested content (e.g. familyInfo: → skip its children)
    if (skipDepth >= 0 && indent > skipDepth) continue;
    else skipDepth = -1;

    // List item continuation
    if (trimmed.startsWith('- ') || trimmed.startsWith('-  ')) {
      const item = trimmed.replace(/^-\s*/, '').replace(/^"/, '').replace(/"$/, '').trim();
      if (currentList !== null) {
        currentList.push(item);
      }
      continue;
    }

    // Continuation of multiline value (> or |)
    if (currentMultilineKey && (trimmed && !trimmed.includes(':') || trimmed.startsWith(' '))) {
      currentMultilineLines.push(trimmed);
      continue;
    }

    // End multiline context
    if (currentMultilineKey) {
      data[currentMultilineKey] = currentMultilineLines.join(' ').trim();
      currentMultilineKey = null;
      currentMultilineLines = [];
    }
    // End list context (non-list item starts new key)
    if (currentList !== null && !trimmed.startsWith('- ')) {
      currentList = null;
      currentListKey = null;
    }

    // Key: value
    const colonIdx = trimmed.indexOf(':');
    if (colonIdx === -1) continue;

    const key = trimmed.substring(0, colonIdx).trim();
    let value = trimmed.substring(colonIdx + 1).trim();

    // Handle quoted strings
    if (value.startsWith('"') && value.endsWith('"')) {
      value = value.slice(1, -1);
    } else if (value.startsWith("'") && value.endsWith("'")) {
      value = value.slice(1, -1);
    }

    // Handle folded scalar (>)
    if (value === '>') {
      currentMultilineKey = key;
      currentMultilineLines = [];
      continue;
    }

    // Handle literal scalar (|)
    if (value === '|') {
      currentMultilineKey = key;
      currentMultilineLines = [];
      continue;
    }

    // Handle numbers
    if (/^-?\d+(\.\d+)?$/.test(value)) {
      value = Number(value);
    }

    // Handle booleans
    if (value === 'true' || value === 'false') {
      value = value === 'true';
    }

    // Handle empty value → start of a list or nested object
    if (value === '' || value === undefined) {
      const nextLine = i + 1 < fmLines.length ? fmLines[i + 1] : '';
      const nextTrimmed = nextLine.trim();
      const nextIndent = nextLine.length - nextLine.trimStart().length;
      if (nextTrimmed.startsWith('- ')) {
        currentList = [];
        currentListKey = key;
        data[key] = currentList;
      } else if (nextIndent > indent) {
        // nested object — skip all children at deeper indent
        skipDepth = indent;
      }
      continue;
    }

    data[key] = value;
  }

  // Finalize any pending multiline
  if (currentMultilineKey) {
    data[currentMultilineKey] = currentMultilineLines.join(' ').trim();
  }

  return { data, body };
}

// ─── Collect MD files ───
function collectMD(dir) {
  const result = [];
  try {
    const entries = fs.readdirSync(dir);
    for (const entry of entries) {
      const full = path.join(dir, entry);
      const stat = fs.statSync(full);
      if (stat.isDirectory()) {
        result.push(...collectMD(full));
      } else if (entry.endsWith('.md')) {
        result.push(full);
      }
    }
  } catch (e) {
    console.warn(`  WARNING: Cannot read ${dir}: ${e.message}`);
  }
  return result;
}

// ─── Build products.json ───
function buildProducts() {
  const productsDir = path.join(CONTENT_DIR, 'products');
  const mdFiles = collectMD(productsDir);
  console.log(`  Found ${mdFiles.length} product MD files`);

  // Organize by family
  const families = {
    'strip-plank': { id: 'strip-plank', name: 'Strip Plank', chineseName: '条板', description: 'The quiet luxury of restraint. Long lines, expanded space. Less, perfected.', eyebrow: 'The Purist', stats: '', coverImage: '/images/products/strip-plank/Budelli/1.jpg', items: [] },
    'chevron': { id: 'chevron', name: 'Chevron', chineseName: '鱼骨拼', description: 'Bold angles that command the room. For spaces that deserve to be unforgettable.', eyebrow: 'The Statement', stats: '', coverImage: '/images/products/chevron/Capraia/1.jpg', items: [] },
    'herringbone': { id: 'herringbone', name: 'Herringbone', chineseName: '人字拼', description: 'Parquetry reimagined as olfactory art. A silent symphony of wood and light.', eyebrow: 'The Classic', stats: '', coverImage: '/images/products/herringbone/Comacina/1.jpg', items: [] },
  };

  for (const mdFile of mdFiles) {
    const raw = fs.readFileSync(mdFile, 'utf8');
    const { data: meta } = parseFrontmatter(raw);
    const family = meta.family || 'strip-plank';

    const item = {
      id: meta.id || path.basename(mdFile, '.md'),
      code: meta.code || meta.name || '',
      name: meta.name || '',
      family: family,
      imageCount: meta.imageCount || 5,
      imagePath: meta.imagePath || `images/products/${family}/${meta.name || ''}/{n}.jpg`,
      status: meta.status === 'active' && meta.published !== false ? 'active' : 'inactive',
      description: meta.description || '',
      details: meta.features ? { features: Array.isArray(meta.features) ? meta.features : [meta.features] } : {},
      createdAt: meta.createdAt || '2024-01-01',
      hasPanorama: meta.hasPanorama || false,
      panoramaPath: meta.panoramaPath || '',
    };

    if (meta.chineseName) item.chineseName = meta.chineseName;

    if (families[family]) {
      families[family].items.push(item);
    }
  }

  // Set stats
  for (const key of Object.keys(families)) {
    families[key].stats = `${families[key].items.length} styles`;
  }

  return {
    products: families,
    metadata: {
      lastUpdated: new Date().toISOString(),
      version: '2.0.0',
      totalProducts: Object.values(families).reduce((sum, f) => sum + f.items.length, 0),
    },
  };
}

// ─── Build journal.json ───
function buildJournal() {
  const journalDir = path.join(CONTENT_DIR, 'journal');
  const mdFiles = collectMD(journalDir);
  console.log(`  Found ${mdFiles.length} journal MD files`);

  const articles = [];
  const categories = new Set();

  for (const mdFile of mdFiles) {
    const raw = fs.readFileSync(mdFile, 'utf8');
    const { data: meta, body } = parseFrontmatter(raw);

    const article = {
      id: meta.id || meta.slug || path.basename(mdFile, '.md'),
      slug: meta.slug || path.basename(mdFile, '.md'),
      title: meta.title || '',
      chineseTitle: meta.chineseTitle || '',
      tag: meta.tag || '',
      chineseTag: meta.chineseTag || '',
      image: meta.image || '',
      date: meta.date || '',
      displayDate: meta.displayDate || meta.date || '',
      status: meta.status || 'draft',
      excerpt: meta.excerpt || '',
      content: body || '',
      author: meta.author || 'GARASTOR Editorial',
      readTime: meta.readTime || '5 min read',
      createdAt: meta.createdAt || meta.date || '',
      updatedAt: meta.updatedAt || meta.date || '',
    };

    if (article.tag) categories.add(article.tag);
    articles.push(article);
  }

  // Sort by date descending
  articles.sort((a, b) => (b.date || '').localeCompare(a.date || ''));

  return {
    articles,
    metadata: {
      lastUpdated: new Date().toISOString(),
      version: '2.0.0',
      totalArticles: articles.length,
      categories: Array.from(categories),
    },
  };
}

// ─── MAIN ───
function main() {
  console.log('═'.repeat(50));
  console.log('  GARASTOR Content Builder v2.0');
  console.log('  MD → JSON compiler for static site');
  console.log('═'.repeat(50));

  // Ensure data directory
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    console.log('  Created data/ directory');
  }

  // Build products
  console.log('\n[Building products.json]');
  const products = buildProducts();
  const productsPath = path.join(DATA_DIR, 'products.json');
  fs.writeFileSync(productsPath, JSON.stringify(products, null, 2), 'utf8');
  console.log(`  Written: ${productsPath} (${products.metadata.totalProducts} products)`);

  // Build journal
  console.log('\n[Building journal.json]');
  const journal = buildJournal();
  const journalPath = path.join(DATA_DIR, 'journal.json');
  fs.writeFileSync(journalPath, JSON.stringify(journal, null, 2), 'utf8');
  console.log(`  Written: ${journalPath} (${journal.metadata.totalArticles} articles)`);

  console.log(`\n{'═'.repeat(50)}`);
  console.log('  BUILD COMPLETE');
  console.log(`  ${products.metadata.totalProducts} products + ${journal.metadata.totalArticles} articles ready`);
  console.log('═'.repeat(50));
}

main();