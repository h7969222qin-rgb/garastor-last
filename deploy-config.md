# GARASTOR Deployment Configuration Guide

This document outlines the complete deployment setup for the GARASTOR website using Decap CMS, GitHub, and Cloudflare Pages.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Decap CMS     │    │   GitHub        │    │   Cloudflare    │    │   Live Website  │
│   Admin         │────│   Repository    │────│   Pages         │────│   (CDN)         │
│   Interface     │    │   (JSON Data)   │    │   (Build/Deploy)│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Phase 1: GitHub Repository Setup

### Initial Commit
1. Create a new GitHub repository: `garastor`
2. Initialize with the existing project files:
   ```bash
   # Clone the empty repo
   git clone https://github.com/yourusername/garastor.git
   cd garastor
   
   # Copy all files from the dist folder
   cp -r /path/to/dist/* .
   
   # Initial commit
   git add .
   git commit -m "Initial commit: GARASTOR website with Decap CMS integration"
   git push origin main
   ```

### Repository Structure
```
garastor/
├── index.html                 # Homepage
├── products.html              # Products page (dynamically loads from /data/products.json)
├── journal.html              # Journal page (dynamically loads from /data/journal.json)
├── admin/                    # Decap CMS admin interface
│   ├── index.html           # Admin dashboard
│   ├── config.yml           # CMS configuration
│   └── decap-setup.html     # CMS setup page
├── data/                     # Content repository (JSON files)
│   ├── products.json        # All product data
│   ├── journal.json         # All journal articles
│   └── collections.json     # Product collections metadata
├── assets/                   # JS/CSS assets
│   ├── data-loader.js       # Dynamic data loading script
│   └── admin-styles.css     # Admin-specific styles
├── css/                      # Main website styles
├── js/                       # Main website scripts
├── images/                   # All images
└── journal/                  # Journal article pages
```

## Phase 2: Cloudflare Pages Setup

### 1. Connect GitHub Repository
1. Go to [Cloudflare Pages Dashboard](https://dash.cloudflare.com/?to=/:account/pages)
2. Click "Create a project" → "Connect to Git"
3. Select your `garastor` repository
4. Choose "main" branch

### 2. Build Settings
- **Framework preset:** None (Static Site)
- **Build command:** (Leave empty - static site)
- **Build output directory:** `/` (root)
- **Root directory:** `/`
- **Environment variables:** (None required for static site)

### 3. Custom Domain (Optional)
1. Add your domain: `garastor.com` (or subdomain)
2. Follow Cloudflare's DNS configuration instructions
3. Enable HTTPS automatically

### 4. Automatic Deployments
- Every push to `main` branch triggers automatic deployment
- Builds typically complete in 1-2 minutes
- Previous deployments are kept for rollback

## Phase 3: Decap CMS Configuration

### 1. Authentication Setup
**Option A: Netlify Identity (Simpler)**
1. Host the site on Netlify instead of Cloudflare
2. Enable Identity service
3. Configure GitHub OAuth

**Option B: GitHub OAuth App**
1. Create new GitHub OAuth App:
   - Developer Settings → OAuth Apps → New OAuth App
   - Homepage URL: `https://your-site.com`
   - Authorization callback URL: `https://your-site.com/admin/`
2. Get Client ID and Client Secret
3. Add to Decap CMS configuration

### 2. Decap CMS Config
The configuration is already set up in `admin/config.yml`:
```yaml
backend:
  name: git-gateway           # For Netlify
  # OR
  name: github                # For GitHub OAuth
  repo: yourusername/garastor # Update with your repo
  branch: main
  auth_scope: repo            # Required for GitHub backend
```

### 3. Test CMS Access
1. Visit `https://your-site.com/admin/`
2. Login with GitHub credentials
3. Verify you can:
   - Add/edit products
   - Create journal articles
   - Upload images
   - Publish changes

## Phase 4: Workflow Integration

### Automated Deployment Pipeline
```yaml
# .github/workflows/deploy.yml (if not using Cloudflare Pages native integration)
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: garastor
          directory: .
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

### Git Backend Behavior
When content is edited via Decap CMS:
1. CMS creates a new commit with JSON updates
2. Commit is pushed directly to GitHub repository
3. Cloudflare Pages detects change and triggers rebuild
4. Site is rebuilt with updated content
5. New version is deployed globally via CDN

## Phase 5: Content Management Workflow

### For Content Editors
1. **Access:** Visit `your-site.com/admin/`
2. **Login:** Use GitHub account
3. **Edit:**
   - Products → Edit product info, toggle visibility
   - Journal → Write articles, set publish dates
4. **Save:** Changes create Git commits
5. **Publish:** Site auto-updates in 1-2 minutes

### For Administrators
1. **Review:** Check content changes in Git history
2. **Revert:** Use Git to revert unwanted changes
3. **Backup:** JSON files provide full content backup
4. **Monitor:** Check Cloudflare Pages build status

## Troubleshooting

### Common Issues

1. **CMS Authentication Fails**
   - Check OAuth App callback URLs
   - Verify repository permissions
   - Ensure correct backend configuration

2. **Builds Fail on Cloudflare**
   - Check build logs in Cloudflare dashboard
   - Verify no missing files or dependencies
   - Ensure proper file paths for images

3. **JSON Data Not Loading**
   - Check browser console for fetch errors
   - Verify CORS configuration (if needed)
   - Ensure JSON files are valid

4. **Images Not Uploading**
   - Check media_folder configuration
   - Verify repository has proper image folders
   - Check file permissions

### Performance Optimization

1. **Image Optimization**
   - Use WebP format for better compression
   - Implement lazy loading
   - Use Cloudflare Image Optimization

2. **Caching Strategy**
   - Set proper cache headers for JSON files
   - Use Cloudflare CDN caching
   - Implement browser cache for assets

3. **Security**
   - Limit admin access to authorized users
   - Enable Cloudflare WAF rules
   - Regular security updates

## Monitoring and Maintenance

### Regular Checks
1. **Build Status:** Monitor Cloudflare Pages build logs
2. **Content Review:** Weekly review of new content
3. **Performance:** Monitor Core Web Vitals
4. **SEO:** Check Google Search Console

### Backup Strategy
1. **Daily:** GitHub repository automatically backs up
2. **Monthly:** Export JSON data manually
3. **Quarterly:** Full site backup including images

## Support and Resources

- **Decap CMS Documentation:** https://decapcms.org/docs/
- **Cloudflare Pages:** https://developers.cloudflare.com/pages/
- **GitHub Actions:** https://docs.github.com/en/actions
- **Project Repository:** https://github.com/yourusername/garastor

---
**Last Updated:** July 13, 2026
**Version:** 1.0.0
**Status:** Ready for Deployment