#!/usr/bin/env python3
import re
from pathlib import Path

def fix_all_page_banners():
    """Fix all pages that are incorrectly using banner.gif instead of proper page images"""
    pages_dir = Path("pages")
    assets_dir = Path("assets/images")
    
    print("🔧 FIXING ALL PAGE BANNER ISSUES")
    print("=" * 40)
    print("Many pages are using small banner.gif instead of proper page images")
    print("Restoring each page to use its correct image file")
    
    fixed_count = 0
    files_modified = []
    
    # Find all HTML files using banner.gif incorrectly
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
            
            # Check if this file uses banner.gif
            if '../assets/images/banner.gif' not in content:
                continue
                
            print(f"\n🔍 Processing: {html_file.name}")
            
            # Get the base filename without extension
            base_name = html_file.stem
            
            # Look for page-specific img0.gif files
            possible_images = [
                f"{base_name}_img0.gif",  # page-specific img0
                "img0.gif"  # local img0.gif
            ]
            
            # Check which image file exists
            correct_image = None
            
            # First check in assets/images for page-specific
            for img_name in possible_images[:-1]:  # Exclude the local img0.gif for now
                if (assets_dir / img_name).exists():
                    correct_image = f"../assets/images/{img_name}"
                    print(f"   ✅ Found page-specific image: {img_name}")
                    break
            
            # If no page-specific image, check for local img0.gif
            if not correct_image and (pages_dir / "img0.gif").exists():
                correct_image = "img0.gif"
                print(f"   ✅ Using local img0.gif")
            
            # If still no specific image found, keep banner.gif but note it
            if not correct_image:
                print(f"   ⚠️  No specific image found, keeping banner.gif")
                continue
            
            # Replace banner.gif with the correct image
            original_content = content
            
            # Find and replace the banner.gif reference
            banner_pattern = r'src="../assets/images/banner\.gif"'
            if re.search(banner_pattern, content):
                content = re.sub(banner_pattern, f'src="{correct_image}"', content)
                
                # Write the updated content
                html_file.write_text(content, encoding='utf-8')
                fixed_count += 1
                files_modified.append(html_file.name)
                print(f"   🔧 Fixed: banner.gif → {correct_image}")
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {e}")
            continue
    
    print(f"\n🎯 BANNER FIX SUMMARY:")
    print(f"✅ Pages fixed: {fixed_count}")
    print(f"✅ Files modified: {len(files_modified)}")
    
    if files_modified:
        print(f"\n📁 Modified files:")
        for file in files_modified[:10]:  # Show first 10
            print(f"   - {file}")
        if len(files_modified) > 10:
            print(f"   ... and {len(files_modified) - 10} more")
    
    return fixed_count > 0

def verify_banner_fixes():
    """Verify that banner fixes are working"""
    pages_dir = Path("pages")
    
    print(f"\n🔍 VERIFYING BANNER FIXES...")
    
    # Count remaining banner.gif usage
    banner_count = 0
    img0_count = 0
    specific_img_count = 0
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            if '../assets/images/banner.gif' in content:
                banner_count += 1
            if 'img0.gif' in content:
                img0_count += 1
            if '_img0.gif' in content:
                specific_img_count += 1
                
        except Exception as e:
            continue
    
    print(f"📊 Current image usage:")
    print(f"   - Pages still using banner.gif: {banner_count}")
    print(f"   - Pages using img0.gif: {img0_count}")
    print(f"   - Pages using page-specific images: {specific_img_count}")
    
    return banner_count

if __name__ == "__main__":
    # Fix all banner issues
    fixed = fix_all_page_banners()
    
    # Verify fixes
    remaining_banners = verify_banner_fixes()
    
    if fixed:
        print(f"\n🚀 SUCCESS! Fixed widespread banner image issues!")
        print("Pages now use their correct images instead of generic banner.gif")
        print("\nReady to commit these important fixes!")
    else:
        print(f"\n📝 No banner fixes were needed")
        
    if remaining_banners == 0:
        print(f"\n✅ Perfect! No pages are using incorrect banner.gif anymore")
    else:
        print(f"\n⚠️  {remaining_banners} pages still using banner.gif (may be intentional)") 