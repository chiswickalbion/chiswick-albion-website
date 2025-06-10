#!/usr/bin/env python3
import os
import re
from pathlib import Path

def check_broken_links():
    pages_dir = Path("pages")
    
    # Find all HTML files with 404 errors
    broken_files = []
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            if "404: Page not found" in content:
                broken_files.append(html_file.name)
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    # Find all internal links in working HTML files
    all_links = set()
    working_files = []
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            if "404: Page not found" not in content:
                working_files.append(html_file.name)
                # Extract href links to .html files (not external URLs)
                links = re.findall(r'href="([^"]*\.html)"', content)
                for link in links:
                    if not link.startswith('http'):
                        all_links.add(link)
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    print("=== BROKEN LINK ANALYSIS ===\n")
    
    print(f"📊 SUMMARY:")
    print(f"- Total HTML files: {len(list(pages_dir.glob('*.html')))}")
    print(f"- Files with 404 errors: {len(broken_files)}")
    print(f"- Working files: {len(working_files)}")
    print(f"- Unique internal links found: {len(all_links)}")
    
    print(f"\n🚫 FILES WITH 404 ERRORS ({len(broken_files)}):")
    for file in sorted(broken_files):
        print(f"   - {file}")
    
    print(f"\n🔗 INTERNAL LINKS REFERENCED:")
    for link in sorted(all_links):
        exists = (pages_dir / link).exists()
        has_404 = False
        if exists:
            try:
                content = (pages_dir / link).read_text(encoding='utf-8', errors='ignore')
                has_404 = "404: Page not found" in content
            except:
                pass
        
        status = "✅ OK" if exists and not has_404 else "❌ BROKEN" if has_404 else "❓ MISSING"
        print(f"   {status} {link}")

if __name__ == "__main__":
    check_broken_links() 