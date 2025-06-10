#!/usr/bin/env python3
import json
from pathlib import Path

def create_validation_dashboard():
    """Create a comprehensive validation dashboard"""
    
    print("📊 CHISWICK ALBION WEBSITE VALIDATION DASHBOARD")
    print("=" * 60)
    print("🎯 Systematic comparison: New GitHub Pages site vs Original site")
    print()
    
    # Load all test results
    reports = {}
    report_files = [
        ('master_validation_report.json', 'Master Validation'),
        ('functional_test_results.json', 'Functional Tests'),
        ('site_comparison_report.json', 'Site Comparison')
    ]
    
    for filename, report_name in report_files:
        if Path(filename).exists():
            with open(filename, 'r') as f:
                reports[report_name] = json.load(f)
        else:
            print(f"⚠️  {report_name} not found: {filename}")
    
    if 'Master Validation' in reports:
        master = reports['Master Validation']
        
        print("🏆 OVERALL ASSESSMENT")
        print("-" * 25)
        assessment = master.get('overall_assessment', {})
        print(f"📊 Overall Score: {assessment.get('overall_score', 'N/A')}%")
        print(f"🎯 Status: {assessment.get('readiness', 'N/A')} - {assessment.get('status', 'N/A')}")
        print(f"💬 {assessment.get('message', 'No message available')}")
        print()
        
        print("📈 DETAILED BREAKDOWN")
        print("-" * 25)
        component_scores = assessment.get('component_scores', {})
        print(f"🧪 Functional Testing: {component_scores.get('functional', 'N/A'):.1f}%")
        print(f"🔍 Site Comparison: {component_scores.get('comparison', 'N/A'):.1f}%")
        print(f"📝 Content Quality: {component_scores.get('content', 'N/A'):.1f}%")
        print(f"⚠️  Error Penalty: {component_scores.get('error_penalty', 'N/A'):.1f}%")
        print()
    
    # Site Statistics
    if 'Master Validation' in reports:
        stats = reports['Master Validation'].get('test_results', {}).get('statistics', {})
        
        print("📊 SITE STATISTICS")
        print("-" * 20)
        print(f"📄 Total HTML Pages: {stats.get('total_html_files', 'N/A'):,}")
        print(f"🖼️  Total Images: {stats.get('total_image_files', 'N/A'):,}")
        print(f"💾 Content Size: {stats.get('total_content_size_mb', 'N/A')} MB")
        print(f"✅ Working Pages: {stats.get('pages_with_content', 'N/A'):,} ({stats.get('content_ratio', 'N/A')}%)")
        print(f"❌ Error Pages: {stats.get('pages_with_404', 'N/A')}")
        print()
    
    # Functional Test Details
    if 'Functional Tests' in reports:
        functional = reports['Functional Tests']
        
        print("🧪 FUNCTIONAL TEST RESULTS")
        print("-" * 30)
        
        test_areas = [
            ('navigation_test', 'Navigation Structure'),
            ('image_map_test', 'Image Maps'),
            ('external_links_test', 'External Links'),
            ('banner_consistency_test', 'Banner Consistency'),
            ('content_completeness_test', 'Content Completeness'),
            ('file_structure_test', 'File Structure')
        ]
        
        for test_key, test_name in test_areas:
            if test_key in functional:
                test_data = functional[test_key]
                if test_key == 'navigation_test':
                    found = test_data.get('critical_pages_found', 0)
                    total = test_data.get('critical_pages_total', 0)
                    status = "✅ PASS" if found == total else "❌ FAIL"
                    print(f"{status} {test_name}: {found}/{total} critical pages")
                
                elif test_key == 'image_map_test':
                    working = test_data.get('working_areas', 0)
                    total = test_data.get('total_areas', 0)
                    status = "✅ PASS" if working == total else "❌ FAIL"
                    print(f"{status} {test_name}: {working}/{total} areas working")
                
                elif test_key == 'external_links_test':
                    found = len(test_data.get('found_domains', []))
                    expected = len(test_data.get('expected_domains', []))
                    status = "✅ PASS" if found >= expected * 0.8 else "❌ FAIL"
                    print(f"{status} {test_name}: {found}/{expected} domains found")
                
                elif test_key == 'content_completeness_test':
                    complete = test_data.get('complete_pages', 0)
                    total = test_data.get('total_pages', 0)
                    ratio = (complete / total * 100) if total > 0 else 0
                    status = "✅ PASS" if ratio >= 95 else "❌ FAIL"
                    print(f"{status} {test_name}: {complete}/{total} pages ({ratio:.1f}%)")
                
                else:
                    print(f"ℹ️  {test_name}: Available")
        print()
    
    # Recommendations
    if 'Master Validation' in reports:
        recommendations = reports['Master Validation'].get('recommendations', [])
        
        high_priority = [r for r in recommendations if r.get('priority') == 'HIGH']
        medium_priority = [r for r in recommendations if r.get('priority') == 'MEDIUM']
        success_items = [r for r in recommendations if r.get('priority') == 'SUCCESS']
        
        if high_priority:
            print("🚨 HIGH PRIORITY ACTIONS NEEDED")
            print("-" * 35)
            for i, rec in enumerate(high_priority, 1):
                print(f"{i}. {rec.get('category', 'Unknown')}: {rec.get('issue', 'No description')}")
                print(f"   💡 Action: {rec.get('action', 'No action specified')}")
                print()
        
        if medium_priority:
            print("⚠️  MEDIUM PRIORITY IMPROVEMENTS")
            print("-" * 35)
            for i, rec in enumerate(medium_priority, 1):
                print(f"{i}. {rec.get('category', 'Unknown')}: {rec.get('issue', 'No description')}")
                print(f"   💡 Action: {rec.get('action', 'No action specified')}")
                print()
        
        if success_items:
            print("✅ SUCCESS INDICATORS")
            print("-" * 20)
            for rec in success_items:
                print(f"✅ {rec.get('action', 'Success item')}")
            print()
    
    # Final Summary
    print("🎯 SUMMARY & NEXT STEPS")
    print("-" * 25)
    
    if 'Master Validation' in reports:
        overall_score = reports['Master Validation'].get('overall_assessment', {}).get('overall_score', 0)
        
        if overall_score >= 90:
            print("🚀 EXCELLENT: Your site is ready for production!")
            print("✅ The new GitHub Pages site is a complete working replacement")
            print("🎉 You can confidently deploy this as your primary website")
        elif overall_score >= 80:
            print("✅ GOOD: Your site is mostly ready with minor issues")
            print("🔧 Address the high-priority actions above")
            print("📅 Consider deploying after fixes, or deploy with monitoring")
        elif overall_score >= 70:
            print("⚠️  FAIR: Your site needs some work before deployment")
            print("🔧 Focus on high and medium priority issues")
            print("📅 Plan to address issues before making this the primary site")
        else:
            print("❌ NEEDS WORK: Significant issues need to be addressed")
            print("🔧 Do not deploy as primary site yet")
            print("📅 Work through all high-priority issues first")
        
        print(f"\n📊 Current Score: {overall_score:.1f}%")
        print(f"🎯 Target Score: 85%+ for production readiness")
        
        # Show the URLs
        site_info = reports['Master Validation'].get('site_info', {})
        print(f"\n🌐 WEBSITE URLS:")
        print(f"Original: {site_info.get('original_base', 'N/A')}")
        print(f"New Site: {site_info.get('new_base', 'N/A')}")
        
    else:
        print("❌ No master validation results found. Run master_site_validator.py first.")
    
    print(f"\n📋 DETAILED REPORTS:")
    for filename, report_name in report_files:
        if Path(filename).exists():
            print(f"✅ {filename} - {report_name}")
        else:
            print(f"❌ {filename} - Missing")

def main():
    create_validation_dashboard()

if __name__ == "__main__":
    main() 