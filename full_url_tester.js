const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    validationReport: 'master_validation_report.json',
    outputFile: 'all_working_urls.json'
};

async function loadAllPageNames() {
    try {
        const data = JSON.parse(await fs.readFile(config.validationReport, 'utf8'));
        const pages = new Set();
        
        // Get pages from navigation links
        if (data.test_results?.functional?.navigation_test?.navigation_links) {
            Object.keys(data.test_results.functional.navigation_test.navigation_links).forEach(page => {
                pages.add(page);
            });
        }
        
        // Get pages from banner usage (this has the most complete list)
        if (data.test_results?.functional?.banner_consistency_test?.banner_usage) {
            Object.values(data.test_results.functional.banner_consistency_test.banner_usage).forEach(pageList => {
                pageList.forEach(page => {
                    pages.add(page);
                });
            });
        }
        
        // Get pages from image map test if available
        if (data.test_results?.functional?.image_map_test?.pages_with_maps) {
            Object.keys(data.test_results.functional.image_map_test.pages_with_maps).forEach(page => {
                pages.add(page);
            });
        }
        
        console.log(`Loaded ${pages.size} unique page names from validation report`);
        
        // Convert to URL mappings using directory pattern
        const urlMappings = Array.from(pages)
            .filter(page => page.endsWith('.html')) // Only HTML files
            .filter(page => !page.includes('../')) // Skip relative paths
            .map(page => {
                const baseName = page.replace('.html', '');
                return {
                    pageName: page,
                    url: `${config.baseUrl}${baseName}/`,
                    baseName: baseName
                };
            });
        
        console.log(`Created ${urlMappings.length} URL mappings for testing`);
        return urlMappings;
    } catch (error) {
        console.error('Error loading page names:', error.message);
        return [];
    }
}

async function testUrl(page, url) {
    try {
        const response = await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 8000
        });
        
        if (response && response.status() === 200) {
            const title = await page.title();
            const bodyText = await page.evaluate(() => 
                document.body ? document.body.innerText.trim() : ''
            );
            
            // Accept page if it has content OR if it has a meaningful title
            if (bodyText.length > 5 || (title && title.length > 0 && title !== 'Untitled')) {
                return { success: true, title, contentLength: bodyText.length };
            } else {
                return { success: false, status: `200 but no content or title (${bodyText.length} chars, title: "${title}")` };
            }
        }
        return { success: false, status: response ? response.status() : 'No response' };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function testAllUrls() {
    console.log('Starting comprehensive URL testing...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    const urlMappings = await loadAllPageNames();
    const workingUrls = [];
    const failedUrls = [];
    const results = {
        tested: 0,
        working: 0,
        failed: 0
    };
    
    console.log(`Testing ${urlMappings.length} URLs...`);
    
    for (const mapping of urlMappings) {
        console.log(`\n[${results.tested + 1}/${urlMappings.length}] Testing: ${mapping.pageName}`);
        console.log(`  URL: ${mapping.url}`);
        
        const result = await testUrl(page, mapping.url);
        
        if (result.success) {
            console.log(`  ✓ SUCCESS: ${result.title} (${result.contentLength} chars)`);
            workingUrls.push({
                pageName: mapping.pageName,
                baseName: mapping.baseName,
                workingUrl: mapping.url,
                title: result.title,
                contentLength: result.contentLength
            });
            results.working++;
        } else {
            console.log(`  ✗ Failed: ${result.error || result.status}`);
            failedUrls.push({
                pageName: mapping.pageName,
                url: mapping.url,
                error: result.error || result.status
            });
            results.failed++;
        }
        
        results.tested++;
        
        // Save progress every 50 pages
        if (results.tested % 50 === 0) {
            await saveProgress(workingUrls, failedUrls, results);
        }
        
        // Small delay to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    await browser.close();
    await saveProgress(workingUrls, failedUrls, results);
    
    console.log('\n=== URL Testing Complete ===');
    console.log(`Pages tested: ${results.tested}`);
    console.log(`Working URLs found: ${results.working}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Success rate: ${((results.working / results.tested) * 100).toFixed(1)}%`);
}

async function saveProgress(workingUrls, failedUrls, results) {
    const output = {
        timestamp: new Date().toISOString(),
        results: results,
        workingUrls: workingUrls,
        failedUrls: failedUrls.slice(-20) // Keep last 20 failures for debugging
    };
    
    await fs.writeFile(config.outputFile, JSON.stringify(output, null, 2));
    console.log(`\nProgress saved: ${workingUrls.length} working URLs, ${failedUrls.length} failed`);
}

// Run the comprehensive URL testing
testAllUrls().catch(console.error); 