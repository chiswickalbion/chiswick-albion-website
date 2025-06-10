#!/usr/bin/env python3
import re
from pathlib import Path

def main():
    pages_dir = Path('pages')
    print('🔍 FINAL VERIFICATION: External Links Status')
    print('=' * 50)

    # Check for remaining old hosting domains (should be 0)
    old_hosting_domains = ['0002n8y.wcomhost.com', 'web.bethere.co.uk']
    total_old_refs = 0

    for domain in old_hosting_domains:
        domain_refs = 0
        for html_file in pages_dir.glob('*.html'):
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            if domain in content:
                domain_refs += 1
        total_old_refs += domain_refs
        print(f'❌ {domain}: {domain_refs} references (should be 0)')

    # Check for proboards links (should be 2)
    proboards_refs = 0
    proboards_files = []
    for html_file in pages_dir.glob('*.html'):
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        if 'proboards' in content and '404: Page not found' not in content:
            proboards_count = content.count('proboards')
            proboards_refs += proboards_count
            proboards_files.append(f'{html_file.name} ({proboards_count})')

    print(f'✅ Proboards forum links: {proboards_refs} references (should be 2)')
    for file in proboards_files:
        print(f'   📁 {file}')

    # Check for YouTube links (should be preserved)
    youtube_refs = 0
    for html_file in pages_dir.glob('*.html'):
        content = html_file.read_text(encoding='utf-8', errors='ignore')
        if 'youtube' in content.lower() and '404: Page not found' not in content:
            youtube_refs += 1

    print(f'✅ YouTube links preserved: {youtube_refs} files')

    print(f'\n🎯 SUMMARY:')
    print(f'✅ Old hosting domains removed: {total_old_refs == 0}')
    print(f'✅ Proboards forum links preserved: {proboards_refs == 2}')
    print(f'✅ YouTube links preserved: {youtube_refs > 0}')
    
    if total_old_refs == 0 and proboards_refs == 2 and youtube_refs > 0:
        print(f'\n🚀 PERFECT! Website cleanup completed successfully!')
        print('✅ All old hosting references removed')
        print('✅ External forum and video links preserved')
        print('✅ Site is now completely independent while maintaining community connections')

if __name__ == "__main__":
    main() 