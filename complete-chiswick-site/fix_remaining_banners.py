#!/usr/bin/env python3
import re
from pathlib import Path

def fix_remaining_banner_issues():
    """Fix banner issues for files using relative paths like ../assets/images/filename_img0.gif"""
    pages_dir = Path("pages")
    correct_banner_path = "../assets/images/banner.gif"
    
    print("🔧 FIXING REMAINING BANNER ISSUES...")
    
    # Pattern to match banner-sized images with specific filenames ending in _img0.gif
    banner_pattern = r'src="\.\.\/assets\/images\/[^"]*_img0\.gif"'
    
    # Also handle the home page specific case
    home_pattern = r'src="\.\.\/assets\/images\/home_img0\.gif"'
    
    fixed_files = []
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
                
            # Skip if already using correct banner
            if correct_banner_path in content:
                continue
            
            original_content = content
            
            # Replace pattern: ../assets/images/anything_img0.gif -> ../assets/images/banner.gif
            content = re.sub(banner_pattern, f'src="{correct_banner_path}"', content)
            
            # Replace home page specific pattern
            content = re.sub(home_pattern, f'src="{correct_banner_path}"', content)
            
            # Also handle the special encoded filename pattern
            encoded_pattern = r'src="\.\.\/assets\/images\/%3c[^"]*_img0\.gif"'
            content = re.sub(encoded_pattern, f'src="{correct_banner_path}"', content)
            
            # Check if we made changes
            if content != original_content:
                # Write the fixed content
                html_file.write_text(content, encoding='utf-8')
                fixed_files.append(html_file.name)
                print(f"✅ Fixed {html_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    return fixed_files

def verify_banner_fixes():
    """Verify that banner fixes are working by checking key files"""
    test_files = ['videos.html', 'home_.html', 'season2022_.html']
    pages_dir = Path("pages")
    
    print("\n🔍 VERIFYING BANNER FIXES...")
    
    for file_name in test_files:
        file_path = pages_dir / file_name
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if "../assets/images/banner.gif" in content:
                    print(f"✅ {file_name}: Using correct banner")
                else:
                    print(f"❌ {file_name}: Still using incorrect banner")
            except Exception as e:
                print(f"❌ Error checking {file_name}: {e}")

def analyze_banner_usage():
    """Analyze what banner images are being used across the site"""
    pages_dir = Path("pages")
    banner_usage = {}
    
    print("\n📊 ANALYZING BANNER USAGE...")
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
            
            # Look for image sources that could be banners (width/height around 600-900 x 100-150)
            img_matches = re.findall(r'<img[^>]*src="([^"]*)"[^>]*width[^>]*(?:65[0-9]|[6-9][0-9][0-9])[^>]*height[^>]*(?:1[01][0-9]|12[0-9])[^>]*>', content, re.IGNORECASE)
            
            for img_src in img_matches:
                if img_src not in banner_usage:
                    banner_usage[img_src] = []
                banner_usage[img_src].append(html_file.name)
                
        except Exception as e:
            continue
    
    for img_src, files in banner_usage.items():
        print(f"Banner: {img_src} (used in {len(files)} files)")
        if len(files) <= 5:  # Show files if not too many
            for file in files[:5]:
                print(f"   - {file}")

if __name__ == "__main__":
    print("🎯 ADVANCED BANNER FIXER")
    print("=" * 50)
    
    # Fix remaining issues
    fixed_files = fix_remaining_banner_issues()
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Additional files fixed: {len(fixed_files)}")
    
    if fixed_files:
        print("\n🔧 FIXED FILES:")
        for file in fixed_files[:10]:  # Show first 10
            print(f"   - {file}")
        if len(fixed_files) > 10:
            print(f"   ... and {len(fixed_files) - 10} more")
    
    # Verify fixes
    verify_banner_fixes()
    
    # Analyze remaining usage
    analyze_banner_usage()
    
    if fixed_files:
        print(f"\n🚀 SUCCESS! Fixed {len(fixed_files)} additional banner issues!")
        print("Ready to commit these changes!")
    else:
        print("\n📝 No additional banner issues to fix.") 