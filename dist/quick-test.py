#!/usr/bin/env python3
"""
GARASTOR Quick Site Test
Run this to check basic site functionality before deployment
"""

import os
import sys
import json
import http.server
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

class SiteTester:
    def __init__(self, site_path):
        self.site_path = Path(site_path).resolve()
        self.server = None
        self.port = 8080

        print(f"🚀 GARASTOR Site Tester")
        print(f"📁 Testing site at: {self.site_path}")
        print("=" * 60)

    def check_required_files(self):
        """Check if all required files exist"""
        print("🔍 Checking required files...")

        required_files = [
            "index.html",
            "products.html",
            "journal.html",
            "data/products.json",
            "data/journal.json",
            "admin/index.html",
            "css/style.css",
            "images/favicon.svg"
        ]

        all_ok = True
        for file in required_files:
            path = self.site_path / file
            if path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - MISSING")
                all_ok = False

        print()
        return all_ok

    def validate_json(self):
        """Validate JSON files"""
        print("📋 Validating JSON files...")

        json_files = [
            "data/products.json",
            "data/journal.json"
        ]

        all_ok = True
        for json_file in json_files:
            path = self.site_path / json_file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  ✅ {json_file} - Valid JSON ({len(data) if isinstance(data, list) else 'Object'})")
            except json.JSONDecodeError as e:
                print(f"  ❌ {json_file} - Invalid JSON: {e}")
                all_ok = False
            except Exception as e:
                print(f"  ❌ {json_file} - Error: {e}")
                all_ok = False

        print()
        return all_ok

    def check_paths_in_html(self):
        """Check for problematic paths in HTML files"""
        print("🔗 Checking HTML paths...")

        html_files = list(self.site_path.glob("**/*.html"))
        problematic_files = []

        for html_file in html_files[:10]:  # Check first 10 files
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for problematic patterns
                    problems = []
                    if '../' in content:
                        problems.append("Contains '../' relative paths")

                    if html_file.name != 'index.html' and 'href="./' in content:
                        problems.append("Contains './' relative paths")

                    if problems:
                        rel_path = html_file.relative_to(self.site_path)
                        print(f"  ⚠️  {rel_path}")
                        for problem in problems:
                            print(f"     - {problem}")
                        problematic_files.append(str(rel_path))
                    else:
                        rel_path = html_file.relative_to(self.site_path)
                        print(f"  ✅ {rel_path}")

            except Exception as e:
                print(f"  ❌ {html_file.name} - Error reading: {e}")

        print(f"📊 Total HTML files checked: {len(html_files)}")
        print(f"⚠️  Files with path issues: {len(problematic_files)}")
        print()
        return len(problematic_files) == 0

    def check_image_paths(self):
        """Verify image paths referenced in HTML"""
        print("🖼️  Checking image references...")

        # Check a few critical image paths
        critical_images = [
            "images/favicon.svg",
            "images/products/strip-plank/Budelli/1.jpg",
            "images/products/chevron/Capraia/1.jpg",
            "images/products/herringbone/Comacina/1.jpg"
        ]

        missing_images = []
        for img in critical_images:
            path = self.site_path / img
            if path.exists():
                print(f"  ✅ {img}")
            else:
                print(f"  ❌ {img} - MISSING")
                missing_images.append(img)

        print()
        return len(missing_images) == 0

    def run_http_server(self):
        """Start a simple HTTP server for manual testing"""
        print("🌐 Starting HTTP server for manual testing...")

        os.chdir(self.site_path)

        # Start server in background
        handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer(("", self.port), handler)

        def run_server():
            print(f"   Server running at: http://localhost:{self.port}")
            print(f"   Press Ctrl+C to stop")
            self.server.serve_forever()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(1)

        # Open browser to homepage
        print(f"   Opening browser to http://localhost:{self.port}")
        webbrowser.open(f"http://localhost:{self.port}")

        return True

    def check_admin_setup(self):
        """Check Decap CMS admin setup"""
        print("🛠️  Checking Decap CMS setup...")

        admin_files = [
            "admin/index.html",
            "admin/config.yml",
            "admin/decap-setup.html"
        ]

        all_ok = True
        for file in admin_files:
            path = self.site_path / file
            if path.exists():
                size = path.stat().st_size
                print(f"  ✅ {file} ({size:,} bytes)")
            else:
                print(f"  ❌ {file} - MISSING")
                all_ok = False

        # Check config.yml readability
        config_path = self.site_path / "admin/config.yml"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "backend:" in content:
                        print("  ✅ config.yml contains backend configuration")
                    else:
                        print("  ⚠️  config.yml missing backend configuration")
                        all_ok = False
            except Exception as e:
                print(f"  ❌ Error reading config.yml: {e}")
                all_ok = False

        print()
        return all_ok

    def run_deployment_checks(self):
        """Check deployment configuration"""
        print("🚀 Checking deployment configuration...")

        deploy_files = [
            ".github/workflows/cloudflare-deploy.yml",
            "deploy-config.md",
            "site-checks.md"
        ]

        for file in deploy_files:
            path = self.site_path / file
            if path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} - MISSING (not critical)")

        print()
        return True  # Not critical, just informative

    def run_all_tests(self):
        """Run all tests"""
        print("\n🏁 Running comprehensive site tests...")
        print("=" * 60)

        results = {
            "required_files": self.check_required_files(),
            "json_validation": self.validate_json(),
            "html_paths": self.check_paths_in_html(),
            "image_paths": self.check_image_paths(),
            "admin_setup": self.check_admin_setup(),
            "deployment_check": self.run_deployment_checks()
        }

        print("=" * 60)
        print("📊 TEST RESULTS:")
        print("=" * 60)

        passed = 0
        total = len(results)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")
            if result:
                passed += 1

        print("=" * 60)
        print(f"🎯 Score: {passed}/{total} passed")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Site is ready for deployment.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please fix before deployment.")

        return passed == total

    def cleanup(self):
        """Stop the HTTP server if running"""
        if self.server:
            print("\n🛑 Stopping HTTP server...")
            self.server.shutdown()
            self.server.server_close()

def main():
    # Get site path from command line or use current directory
    if len(sys.argv) > 1:
        site_path = sys.argv[1]
    else:
        site_path = os.getcwd()

    tester = SiteTester(site_path)

    try:
        if tester.run_all_tests():
            print("\n🌐 Would you like to start a test server? (y/n): ", end="")
            response = input().strip().lower()

            if response in ['y', 'yes']:
                tester.run_http_server()
                print("\n🔧 Manual testing session started.")
                print("   Navigate to http://localhost:8080 to test the site.")
                print("   Check the admin panel at http://localhost:8080/admin/")
                print("   Press Enter to stop testing...")
                input()

        print("\n📝 Next steps:")
        print("1. Review test results above")
        print("2. Fix any issues indicated")
        print("3. Upload to GitHub repository")
        print("4. Connect to Cloudflare Pages")
        print("5. Configure Decap CMS authentication")
        print("6. Update documentation with actual URLs")

    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()