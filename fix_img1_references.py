#!/usr/bin/env python3
"""
Fix img1.gif References
Create page-specific img1.gif files and update all HTML references
"""

import os
import re
import glob
import shutil

def fix_img1_references():
    """Fix all img1.gif references by creating page-specific images"""
    
    pages_dir = 'pages'
    images_dir = 'assets/images'
    base_img1 = f'{images_dir}/img1.gif'
    
    # Ensure base img1.gif exists
    if not os.path.exists(base_img1):
        print(f"❌ Base image {base_img1} not found!")
        return
    
    html_files = glob.glob(f'{pages_dir}/*.html')
    
    print("🔧 FIXING IMG1.GIF REFERENCES")
    print("=" * 50)
    
    total_fixes = 0
    files_fixed = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            page_name = os.path.basename(html_file).replace('.html', '')
            
            # Check if this page uses img1.gif without proper path
            if 'src="img1.gif"' in content:
                # Create page-specific image
                page_img1 = f'{images_dir}/{page_name}_img1.gif'
                if not os.path.exists(page_img1):
                    shutil.copy2(base_img1, page_img1)
                    print(f"📷 Created: {page_img1}")
                
                # Update HTML reference
                content = content.replace('src="img1.gif"', f'src="../assets/images/{page_name}_img1.gif"')
                print(f"📄 Fixed: {html_file} → {page_name}_img1.gif")
                total_fixes += 1
            
            # Also fix any remaining img0.gif without proper path
            if 'src="img0.gif"' in content:
                content = content.replace('src="img0.gif"', 'src="../assets/images/img0.gif"')
                print(f"📄 Fixed img0 path: {html_file}")
                total_fixes += 1
            
            # Write back if changes were made
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_fixed += 1
        
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    print(f"\n✅ IMG1.GIF REFERENCE FIX COMPLETE")
    print(f"📊 Files fixed: {files_fixed}")
    print(f"📊 Total fixes: {total_fixes}")

if __name__ == "__main__":
    fix_img1_references() 