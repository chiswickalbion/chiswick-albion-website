#!/usr/bin/env python3
"""
Fix Legend File References
Systematically replace all %3clegends references with proper legend filenames
"""

import os
import re
import glob

def fix_legend_references():
    """Replace all %3clegends references with proper legend filenames"""
    
    # Mapping of URL-encoded names to proper names
    legend_mappings = {
        '%3clegends.html': 'legends.html',
        '%3clegends_.html': 'legends_.html', 
        '%3clegends_index.html': 'legends_index.html',
        '%3clegends_page2.html': 'legends_page2.html',
        '%3clegends_page3.html': 'legends_page3.html',
        '%3clegends_page4.html': 'legends_page4.html',
        '%3clegends_page5.html': 'legends_page5.html',
        '%3clegends_page6.html': 'legends_page6.html',
    }
    
    # Also fix image references
    image_mappings = {
        '%3clegends_img': 'legends_img'
    }
    
    pages_dir = 'pages'
    html_files = glob.glob(f'{pages_dir}/*.html')
    
    total_replacements = 0
    files_modified = 0
    
    print("🔧 FIXING LEGEND REFERENCES")
    print("=" * 50)
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            # Replace HTML file references
            for old_ref, new_ref in legend_mappings.items():
                count = content.count(old_ref)
                if count > 0:
                    content = content.replace(old_ref, new_ref)
                    file_replacements += count
                    print(f"   📄 {os.path.basename(html_file)}: {old_ref} → {new_ref} ({count} times)")
            
            # Replace image references
            for old_img, new_img in image_mappings.items():
                count = content.count(old_img)
                if count > 0:
                    content = content.replace(old_img, new_img)
                    file_replacements += count
                    print(f"   🖼️  {os.path.basename(html_file)}: {old_img} → {new_img} ({count} times)")
            
            # Write back if changes were made
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified += 1
                total_replacements += file_replacements
        
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    print(f"\n✅ LEGEND REFERENCE FIX COMPLETE")
    print(f"📊 Files modified: {files_modified}")
    print(f"📊 Total replacements: {total_replacements}")

if __name__ == "__main__":
    fix_legend_references() 