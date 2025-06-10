#!/usr/bin/env python3
import re
from pathlib import Path

OLD_DOMAIN = "0002n8y.wcomhost.com"
OLD_BASE_URL = f"https://{OLD_DOMAIN}/website"
OLD_HTTP_URL = f"http://{OLD_DOMAIN}/website"

def find_old_website_references():
    """Find all references to the old website"""
    pages_dir = Path("pages")
    
    print("🔍 SCANNING FOR OLD WEBSITE REFERENCES...")
    print(f"Looking for: {OLD_DOMAIN}")
    
    references = []
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Skip 404 pages
            if "404: Page not found" in content:
                continue
            
            # Find all references to the old domain
            old_refs = []
            
            # Look for full URLs
            https_matches = re.findall(rf'https://{re.escape(OLD_DOMAIN)}[^"\s]*', content)
            http_matches = re.findall(rf'http://{re.escape(OLD_DOMAIN)}[^"\s]*', content)
            
            # Look for just domain references
            domain_matches = re.findall(rf'{re.escape(OLD_DOMAIN)}[^"\s]*', content)
            
            all_matches = set(https_matches + http_matches + domain_matches)
            
            if all_matches:
                references.append({
                    'file': html_file.name,
                    'matches': list(all_matches),
                    'content': content
                })
                
                print(f"❌ {html_file.name}:")
                for match in all_matches:
                    print(f"   - {match}")
                    
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
    
    return references

def remove_old_website_references(references):
    """Remove or replace old website references"""
    pages_dir = Path("pages")
    fixed_files = []
    
    print(f"\n🔧 REMOVING OLD WEBSITE REFERENCES...")
    
    for ref_info in references:
        file_name = ref_info['file']
        matches = ref_info['matches']
        content = ref_info['content']
        
        try:
            new_content = content
            changes_made = False
            
            for match in matches:
                print(f"🔧 Processing {file_name}: {match}")
                
                # Strategy 1: Remove href attributes that point to old site
                # Replace href="old_url" with href="#" or remove the link
                old_href_pattern = rf'href="{re.escape(match)}"'
                if re.search(old_href_pattern, new_content):
                    new_content = re.sub(old_href_pattern, 'href="#"', new_content)
                    print(f"   ✅ Replaced href link with #")
                    changes_made = True
                
                # Strategy 2: Remove any direct text references
                if match in new_content:
                    # For area shape links, just disable them
                    area_pattern = rf'<area[^>]*href="{re.escape(match)}"[^>]*>'
                    area_matches = re.findall(area_pattern, new_content)
                    for area_match in area_matches:
                        # Replace with disabled area (no href)
                        disabled_area = re.sub(r'href="[^"]*"', '', area_match)
                        new_content = new_content.replace(area_match, disabled_area)
                        print(f"   ✅ Disabled area map link")
                        changes_made = True
                    
                    # For any remaining direct references, comment them out
                    remaining_pattern = rf'https?://{re.escape(OLD_DOMAIN)}[^"\s]*'
                    remaining_matches = re.findall(remaining_pattern, new_content)
                    for remaining in remaining_matches:
                        new_content = new_content.replace(remaining, f"<!-- REMOVED: {remaining} -->")
                        print(f"   ✅ Commented out reference")
                        changes_made = True
            
            if changes_made:
                # Write the cleaned content
                file_path = pages_dir / file_name
                file_path.write_text(new_content, encoding='utf-8')
                fixed_files.append(file_name)
                print(f"✅ Cleaned {file_name}")
            
        except Exception as e:
            print(f"❌ Error fixing {file_name}: {e}")
    
    return fixed_files

def verify_cleanup():
    """Verify that old references have been removed"""
    pages_dir = Path("pages")
    
    print("\n🔍 VERIFYING CLEANUP...")
    
    remaining_refs = 0
    
    for html_file in pages_dir.glob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            if OLD_DOMAIN in content:
                # Check if it's just in comments
                non_comment_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                if OLD_DOMAIN in non_comment_content:
                    print(f"⚠️  {html_file.name}: Still contains references to old domain")
                    remaining_refs += 1
                else:
                    print(f"✅ {html_file.name}: References only in comments (OK)")
                    
        except Exception as e:
            continue
    
    if remaining_refs == 0:
        print("🎉 ALL OLD WEBSITE REFERENCES REMOVED!")
    else:
        print(f"⚠️  {remaining_refs} files still have active references")
    
    return remaining_refs == 0

def show_statistics(references):
    """Show statistics about old references found"""
    total_files = len(references)
    total_refs = sum(len(ref['matches']) for ref in references)
    
    print(f"\n📊 REFERENCE STATISTICS:")
    print(f"Files with old references: {total_files}")
    print(f"Total references found: {total_refs}")
    
    # Show most common reference types
    all_refs = []
    for ref in references:
        all_refs.extend(ref['matches'])
    
    ref_counts = {}
    for ref in all_refs:
        ref_counts[ref] = ref_counts.get(ref, 0) + 1
    
    print(f"\nMost common references:")
    for ref, count in sorted(ref_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {count}x: {ref}")

if __name__ == "__main__":
    print("🎯 OLD WEBSITE REFERENCE REMOVER")
    print("=" * 50)
    print(f"Target: Remove all references to {OLD_DOMAIN}")
    
    # Find all references
    references = find_old_website_references()
    
    if not references:
        print("\n✅ No old website references found!")
    else:
        # Show statistics
        show_statistics(references)
        
        # Remove references
        fixed_files = remove_old_website_references(references)
        
        print(f"\n📊 CLEANUP SUMMARY:")
        print(f"✅ Files cleaned: {len(fixed_files)}")
        
        # Verify cleanup
        success = verify_cleanup()
        
        if success and fixed_files:
            print(f"\n🚀 SUCCESS! Removed all references to old website!")
            print("Ready to commit these changes!")
        elif fixed_files:
            print(f"\n⚠️  Partial success - some references may remain") 