#!/bin/bash
# Fix relative paths in journal article HTML files
# Change all ../ references to absolute /

echo "🔧 Fixing relative paths in journal articles..."

# Navigate to journal directory
cd "$(dirname "$0")/journal" || exit

# List of journal article files
files=(
    "agamben-bare-life-form.html"
    "deleuze-fold-floor-leibniz.html"
    "eco-open-work-floor.html"
    "negri-multitude-common-surface.html"
    "schelling-nature-floor-reverence.html"
    "vattimo-weak-thought-floor.html"
)

# Replacement patterns
declare -A replacements=(
    ['href="../images/favicon.svg"']='href="/images/favicon.svg"'
    ['href="../css/style.css"']='href="/css/style.css"'
    ['href="../index.html"']='href="/index.html"'
    ['href="../products.html"']='href="/products.html"'
    ['href="../collections.html"']='href="/collections.html"'
    ['href="../brand-story.html"']='href="/brand-story.html"'
    ['href="../lookbook.html"']='href="/lookbook.html"'
    ['href="../boutiques.html"']='href="/boutiques.html"'
    ['href="../journal.html"']='href="/journal.html"'
    ['href="../contact.html"']='href="/contact.html"'
    ['href="../journal.html"']='href="/journal.html"'
    ['script src="../js/']='script src="/js/'
    ['src="../images/']='src="/images/'
    ["src='../images/"]="src='/images/"
)

# Process each file
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "📄 Processing: $file"

        # Create backup
        cp "$file" "${file}.backup"

        # Apply replacements
        temp_file="${file}.tmp"
        cp "$file" "$temp_file"

        for pattern in "${!replacements[@]}"; do
            replacement="${replacements[$pattern]}"
            # Use sed with proper escaping
            sed -i "s|$pattern|$replacement|g" "$temp_file"
        done

        # Replace original
        mv "$temp_file" "$file"
        echo "✅ Updated: $file"
    else
        echo "⚠️  File not found: $file"
    fi
done

# Also check if any ../ references remain
echo "🔍 Checking for remaining ../ references..."
grep -r "\.\./" . --include="*.html" || echo "✅ No remaining ../ references found"

echo "🎉 Journal paths fixed!"
echo "Backup files created with .backup extension"