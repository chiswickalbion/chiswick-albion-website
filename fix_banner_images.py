#!/usr/bin/env python3
import re
from pathlib import Path
import requests

def analyze_banner_issues():
    """Identify pages with banner image issues"""
    pages_dir = Path("pages")
    correct_banner_path = "../assets/images/banner.gif"
    
    print("🔍 ANALYZING BANNER IMAGE ISSUES...")
    
    # Common banner image patterns that might be incorrect
    banner_patterns = [
        (r'src="img0\.gif"', 'width=659|width="659"', 'height=119|height="119"'),  # videos.html style
        (r'src="img0\.gif"', 'width=658|width="658"', 'height=119|height="119"'),  # slight variations
        (r'src="([^"]*img0\.gif)"', None, None),  # any img0.gif that might be a banner
    ]
    
    problematic_files = []
    
    # Check each HTML file
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
            
            # Check for banner-like image patterns
            for src_pattern, width_pattern, height_pattern in banner_patterns:
                src_matches = re.findall(src_pattern, content)
                
                if src_matches:
                    # If we have width/height patterns, check those too
                    is_banner_sized = True
                    if width_pattern and height_pattern:
                        width_match = re.search(width_pattern, content)
                        height_match = re.search(height_pattern, content)
                        is_banner_sized = bool(width_match and height_match)
                    
                    if is_banner_sized:
                        # Check if it's not already using the correct banner
                        if correct_banner_path not in content:
                            img_ref = src_matches[0] if isinstance(src_matches[0], str) else "img0.gif"
                            problematic_files.append({
                                'file': html_file.name,
                                'current_src': img_ref,
                                'content': content
                            })
                            print(f"❌ {html_file.name}: Using {img_ref} as banner (should be banner.gif)")
                            break
                        
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    return problematic_files

def fix_banner_images(problematic_files):
    """Fix the identified banner image issues"""
    pages_dir = Path("pages")
    correct_banner_path = "../assets/images/banner.gif"
    fixed_count = 0
    
    print(f"\n🔧 FIXING {len(problematic_files)} BANNER ISSUES...")
    
    for file_info in problematic_files:
        file_name = file_info['file']
        current_src = file_info['current_src']
        content = file_info['content']
        
        try:
            # Replace the problematic banner image reference
            # Handle both quoted and unquoted src attributes
            new_content = content
            
            # Pattern 1: src="img0.gif" -> src="../assets/images/banner.gif"
            new_content = re.sub(r'src="img0\.gif"', f'src="{correct_banner_path}"', new_content)
            
            # Pattern 2: Any other img0.gif references in the right context
            new_content = re.sub(r'src="([^"]*/)img0\.gif"', f'src="{correct_banner_path}"', new_content)
            
            if new_content != content:
                # Write the fixed content
                file_path = pages_dir / file_name
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✅ Fixed {file_name}: {current_src} → banner.gif")
                fixed_count += 1
            else:
                print(f"⚠️  {file_name}: No changes made (pattern not matched)")
                
        except Exception as e:
            print(f"❌ Error fixing {file_name}: {e}")
    
    return fixed_count

def verify_banner_exists():
    """Check if the banner file exists"""
    banner_path = Path("assets/images/banner.gif")
    if banner_path.exists():
        print(f"✅ Banner file exists: {banner_path}")
        return True
    else:
        print(f"❌ Banner file missing: {banner_path}")
        return False

def download_banner_if_missing():
    """Download banner from original site if missing"""
    banner_path = Path("assets/images/banner.gif")
    
    if banner_path.exists():
        return True
    
    print("📥 Downloading banner.gif from original site...")
    
    # Try different possible banner URLs
    banner_urls = [
        "https://0002n8y.wcomhost.com/website/assets/images/banner.gif",
        "https://0002n8y.wcomhost.com/website/banner.gif",
        "https://0002n8y.wcomhost.com/website/images/banner.gif"
    ]
    
    for url in banner_urls:
        try:
            print(f"   Trying {url}...", end=" ")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                banner_path.write_bytes(response.content)
                print("✅ SUCCESS")
                return True
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {e}")
    
    print("❌ Could not download banner.gif from original site")
    return False

if __name__ == "__main__":
    print("🎯 BANNER IMAGE FIXER")
    print("=" * 50)
    
    # Check if banner exists, download if needed
    if not verify_banner_exists():
        download_banner_if_missing()
    
    # Analyze issues
    problematic_files = analyze_banner_issues()
    
    if not problematic_files:
        print("\n✅ No banner image issues found!")
    else:
        # Fix the issues
        fixed_count = fix_banner_images(problematic_files)
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ Files fixed: {fixed_count}")
        print(f"📝 Total issues found: {len(problematic_files)}")
        
        if fixed_count > 0:
            print("\n🚀 Ready to commit the banner fixes!") 