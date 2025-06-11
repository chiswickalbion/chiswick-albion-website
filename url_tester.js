const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    validationReport: 'site_comparison_report.json',
    outputFile: 'working_urls.json',
    knownWorkingUrls: [
        'honours/',
        'nextgame/',
        'details/',
        'everyplayer/',
        'top25/'
    ]
};

async function loadPageNames() {
    try {
        const data = JSON.parse(await fs.readFile(config.validationReport, 'utf8'));
        const urlMappings = [];
        
        // Get URLs from page_comparison section
        if (data.page_comparison) {
            Object.entries(data.page_comparison).forEach(([pageName, pageData]) => {
                if (pageData.old_url) {
                    urlMappings.push({
                        pageName: pageName,
                        url: pageData.old_url,
                        accessible: pageData.old_accessible
                    });
                }
            });
        }
        
        console.log(`Loaded ${urlMappings.length} URL mappings from validation report`);
        return urlMappings;
    } catch (error) {
        console.error('Error loading URLs:', error.message);
        return [];
    }
}

async function testUrl(page, url) {
    try {
        const response = await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 10000
        });
        
        if (response && response.status() === 200) {
            // Check if page has actual content
            const title = await page.title();
            const bodyText = await page.evaluate(() => 
                document.body ? document.body.innerText.trim() : ''
            );
            
            console.log(`    Status: 200, Title: "${title}", Content length: ${bodyText.length}`);
            console.log(`    Content preview: "${bodyText.substring(0, 100)}"`);
            
            // Accept page if it has content OR if it has a meaningful title (could be image-only page)
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

async function testUrlFormats() {
    console.log('Starting URL format testing...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    // First test known working URLs
    console.log('\n=== Testing Known Working URLs ===');
    for (const urlPath of config.knownWorkingUrls) {
        const url = config.baseUrl + urlPath;
        console.log(`Testing known URL: ${url}`);
        const result = await testUrl(page, url);
        if (result.success) {
            console.log(`  ✓ SUCCESS: ${result.title} (${result.contentLength} chars)`);
        } else {
            console.log(`  ✗ FAILED: ${result.error || result.status}`);
        }
    }
    
    console.log('\n=== Testing URLs from Comparison Report ===');
    
    const urlMappings = await loadPageNames();
    const workingUrls = [];
    const results = {
        tested: 0,
        working: 0,
        failed: 0,
        formats: {
            html: 0,
            directory: 0
        }
    };
    
    console.log(`Testing ${urlMappings.length} URLs...`);
    
    for (const mapping of urlMappings) {
        console.log(`\n[${results.tested + 1}/${urlMappings.length}] Testing: ${mapping.pageName}`);
        console.log(`  URL: ${mapping.url}`);
        console.log(`  Expected accessible: ${mapping.accessible}`);
        
        const result = await testUrl(page, mapping.url);
        
        if (result.success) {
            const format = mapping.url.endsWith('/') ? 'directory' : 'html';
            console.log(`  ✓ SUCCESS: ${format} format works (${result.title}, ${result.contentLength} chars)`);
            workingUrls.push({
                pageName: mapping.pageName,
                workingUrl: mapping.url,
                format: format,
                title: result.title,
                contentLength: result.contentLength,
                expectedAccessible: mapping.accessible
            });
            results.working++;
            results.formats[format]++;
        } else {
            console.log(`  ✗ Failed: ${result.error || result.status}`);
            results.failed++;
        }
        
        results.tested++;
        
        // Save progress every 50 pages
        if (results.tested % 50 === 0) {
            await saveProgress(workingUrls, results);
        }
        
        // Small delay to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    await browser.close();
    await saveProgress(workingUrls, results);
    
    console.log('\n=== URL Testing Complete ===');
    console.log(`Pages tested: ${results.tested}`);
    console.log(`Working URLs found: ${results.working}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`HTML format: ${results.formats.html}`);
    console.log(`Directory format: ${results.formats.directory}`);
}

async function saveProgress(workingUrls, results) {
    const output = {
        timestamp: new Date().toISOString(),
        results: results,
        workingUrls: workingUrls
    };
    
    await fs.writeFile(config.outputFile, JSON.stringify(output, null, 2));
    console.log(`Progress saved: ${workingUrls.length} working URLs found`);
}

// Run the URL testing
testUrlFormats().catch(console.error); 