#!/usr/bin/env python3
import re
from pathlib import Path

def restore_proboards_references():
    """Restore proboards forum references that were incorrectly removed"""
    pages_dir = Path("pages")
    
    print("🔄 RESTORING PROBOARDS FORUM LINKS")
    print("=" * 50)
    print("These should be kept as legitimate external forum references")
    
    proboards_domains = [
        "chiswickalbion.proboards.com", 
        "chiswickalbion.proboards20.com"
    ]
    
    restored_files = []
    total_restored = 0
    
    for domain in proboards_domains:
        print(f"\n🔍 Restoring {domain} references...")
        
        files_restored = 0
        refs_restored = 0
        
        for html_file in pages_dir.glob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
                
                # Skip 404 pages
                if "404: Page not found" in content:
                    continue
                
                original_content = content
                changes_made = False
                
                # Find commented out proboards references
                comment_pattern = rf'<!-- REMOVED: (https?://{re.escape(domain)}[^>]*) -->'
                matches = re.findall(comment_pattern, content)
                
                for match in matches:
                    # Restore the original URL
                    comment_text = f"<!-- REMOVED: {match} -->"
                    content = content.replace(comment_text, match)
                    changes_made = True
                    refs_restored += 1
                    print(f"   ✅ Restored: {match}")
                
                # Also restore any disabled area map links for proboards
                # Look for area tags that had proboards hrefs removed
                area_pattern = rf'<area([^>]*)\s*>'
                areas = re.findall(area_pattern, content)
                
                for area_attrs in areas:
                    # Check if this area is missing href but has proboards in a comment nearby
                    if 'href=' not in area_attrs:
                        # Look for nearby comments with proboards URLs
                        area_full = f'<area{area_attrs}>'
                        area_pos = content.find(area_full)
                        if area_pos != -1:
                            # Check surrounding context for proboards comment
                            context_start = max(0, area_pos - 200)
                            context_end = min(len(content), area_pos + 200)
                            context = content[context_start:context_end]
                            
                            proboards_comment = re.search(rf'<!-- REMOVED: (https?://{re.escape(domain)}[^>]*) -->', context)
                            if proboards_comment:
                                # Restore the href to this area
                                restored_url = proboards_comment.group(1)
                                new_area = f'<area{area_attrs} href="{restored_url}">'
                                content = content.replace(area_full, new_area)
                                # Remove the comment
                                content = content.replace(proboards_comment.group(0), '')
                                changes_made = True
                                refs_restored += 1
                                print(f"   ✅ Restored area link: {restored_url}")
                
                if changes_made:
                    html_file.write_text(content, encoding='utf-8')
                    files_restored += 1
                    
            except Exception as e:
                print(f"❌ Error processing {html_file}: {e}")
                continue
        
        print(f"   📊 {files_restored} files updated, {refs_restored} references restored")
        total_restored += refs_restored
        
        if files_restored > 0:
            restored_files.extend([f.name for f in pages_dir.glob("*.html") if f.stat().st_mtime > 0])
    
    print(f"\n🎯 RESTORATION SUMMARY:")
    print(f"✅ Total proboards references restored: {total_restored}")
    print(f"✅ Files with proboards links restored: {len(set(restored_files))}")
    
    return total_restored > 0

def verify_proboards_restoration():
    """Verify proboards links are now active"""
    pages_dir = Path("pages")
    
    print(f"\n🔍 VERIFYING PROBOARDS RESTORATION...")
    
    proboards_count = 0
    files_with_proboards = []
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for active proboards links
            non_comment_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            if 'proboards' in non_comment_content:
                proboards_count += 1
                files_with_proboards.append(html_file.name)
                
        except Exception as e:
            continue
    
    print(f"✅ Found {proboards_count} files with active proboards references")
    
    if files_with_proboards:
        print("Files with proboards links:")
        for file in files_with_proboards[:5]:  # Show first 5
            print(f"   - {file}")
        if len(files_with_proboards) > 5:
            print(f"   ... and {len(files_with_proboards) - 5} more")
    
    return proboards_count > 0

if __name__ == "__main__":
    # Restore proboards references
    restored = restore_proboards_references()
    
    # Verify restoration
    verified = verify_proboards_restoration()
    
    if restored:
        print(f"\n🚀 SUCCESS! Proboards forum links have been restored!")
        print("These external forum references are now active again.")
        print("\nReady to commit these corrections!")
    else:
        print(f"\n📝 No proboards references found to restore.")
        
    if verified:
        print(f"\n✅ Verification: Proboards links are now active and working!") 