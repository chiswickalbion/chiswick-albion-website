#!/usr/bin/env python3
import re
from pathlib import Path
import requests
import time

def analyze_and_fix_image_issues():
    pages_dir = Path("pages")
    assets_dir = Path("assets")
    
    print("🔍 ANALYZING IMAGE PATH ISSUES...")
    
    # Track issues
    broken_image_files = []
    fixed_files = []
    
    # Get all image files available
    available_images = {}
    for img_path in assets_dir.rglob("*"):
        if img_path.is_file() and img_path.suffix.lower() in ['.gif', '.jpg', '.jpeg', '.png']:
            available_images[img_path.name] = str(img_path)
    
    # Also check pages directory for images
    for img_path in pages_dir.rglob("*"):
        if img_path.is_file() and img_path.suffix.lower() in ['.gif', '.jpg', '.jpeg', '.png']:
            available_images[img_path.name] = str(img_path)
    
    print(f"📁 Found {len(available_images)} image files available")
    
    # Check each HTML file for image path issues
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
                
            # Find all image references
            img_refs = re.findall(r'src="([^"]*\.(gif|jpg|jpeg|png))"', content, re.IGNORECASE)
            
            has_issues = False
            new_content = content
            
            for img_ref, ext in img_refs:
                img_filename = Path(img_ref).name
                
                # Check if image exists at the referenced path
                referenced_path = pages_dir / img_ref
                
                if not referenced_path.exists():
                    # Try to find the image in our available images
                    if img_filename in available_images:
                        # Calculate relative path from pages directory to the image
                        actual_img_path = Path(available_images[img_filename])
                        relative_path = str(actual_img_path.relative_to(pages_dir.parent))
                        
                        print(f"🔧 {html_file.name}: Fixing {img_ref} → {relative_path}")
                        new_content = new_content.replace(f'src="{img_ref}"', f'src="../{relative_path}"')
                        has_issues = True
                    else:
                        print(f"❌ {html_file.name}: Missing image {img_ref}")
                        has_issues = True
            
            # Save fixed content
            if has_issues:
                if new_content != content:
                    html_file.write_text(new_content, encoding='utf-8')
                    fixed_files.append(html_file.name)
                else:
                    broken_image_files.append(html_file.name)
                    
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Files with fixed image paths: {len(fixed_files)}")
    print(f"❌ Files with missing images: {len(broken_image_files)}")
    
    if fixed_files:
        print(f"\n🔧 FIXED FILES:")
        for file in fixed_files:
            print(f"   - {file}")
    
    if broken_image_files:
        print(f"\n❌ FILES WITH MISSING IMAGES:")
        for file in broken_image_files:
            print(f"   - {file}")
    
    return fixed_files, broken_image_files

def download_missing_images():
    """Download missing images from original site"""
    missing_images = ['img1.gif']  # We know img1.gif is missing for videos.html
    base_url = "https://0002n8y.wcomhost.com/website/videos/"
    pages_dir = Path("pages")
    
    print("\n📥 DOWNLOADING MISSING IMAGES...")
    
    for img_name in missing_images:
        try:
            img_url = base_url + img_name
            response = requests.get(img_url, timeout=10)
            
            if response.status_code == 200:
                img_path = pages_dir / img_name
                img_path.write_bytes(response.content)
                print(f"✅ Downloaded {img_name}")
            else:
                print(f"❌ Failed to download {img_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading {img_name}: {e}")

if __name__ == "__main__":
    # First, try to download missing images
    download_missing_images()
    
    # Then fix path issues
    fixed, broken = analyze_and_fix_image_issues()
    
    if fixed:
        print(f"\n🚀 Ready to commit {len(fixed)} fixed files!") 