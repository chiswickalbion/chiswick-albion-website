const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    workingUrlsFile: 'all_working_urls.json',
    outputFile: 'complete_urls_with_pages.json',
    maxPagesToTest: 20 // Test up to page20.html for each section
};

async function loadWorkingUrls() {
    try {
        const data = JSON.parse(await fs.readFile(config.workingUrlsFile, 'utf8'));
        return data.workingUrls || [];
    } catch (error) {
        console.error('Error loading working URLs:', error.message);
        return [];
    }
}

async function testUrl(page, url) {
    try {
        const response = await page.goto(url, { 
            waitUntil: 'networkidle2',
            timeout: 6000
        });
        
        if (response && response.status() === 200) {
            const title = await page.title();
            const bodyText = await page.evaluate(() => 
                document.body ? document.body.innerText.trim() : ''
            );
            
            // Accept page if it has content OR if it has a meaningful title
            if (bodyText.length > 5 || (title && title.length > 0 && title !== 'Untitled')) {
                return { success: true, title, contentLength: bodyText.length };
            }
        }
        return { success: false, status: response ? response.status() : 'No response' };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function testPaginatedUrls() {
    console.log('Starting paginated URL discovery...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    const workingBaseUrls = await loadWorkingUrls();
    const allUrls = [];
    const results = {
        sectionsProcessed: 0,
        totalUrlsTested: 0,
        totalWorkingUrls: 0,
        sections: {}
    };
    
    console.log(`Testing pagination for ${workingBaseUrls.length} base sections...`);
    
    for (const baseUrl of workingBaseUrls) {
        const sectionName = baseUrl.baseName;
        console.log(`\n=== Section: ${sectionName} ===`);
        console.log(`Base URL: ${baseUrl.workingUrl}`);
        
        const sectionResults = {
            baseUrl: baseUrl.workingUrl,
            basePage: {
                url: baseUrl.workingUrl,
                title: baseUrl.title,
                contentLength: baseUrl.contentLength,
                working: true
            },
            pages: [],
            totalPages: 1 // Count base page
        };
        
        // Add the base URL to our complete list
        allUrls.push({
            sectionName: sectionName,
            url: baseUrl.workingUrl,
            pageNumber: 0, // Base page
            title: baseUrl.title,
            contentLength: baseUrl.contentLength
        });
        
        // Test paginated URLs: page1.html, page2.html, etc.
        for (let pageNum = 1; pageNum <= config.maxPagesToTest; pageNum++) {
            const pageUrl = `${config.baseUrl}${sectionName}/page${pageNum}.html`;
            console.log(`  Testing: page${pageNum}.html`);
            
            const result = await testUrl(page, pageUrl);
            results.totalUrlsTested++;
            
            if (result.success) {
                console.log(`    ✓ SUCCESS: ${result.title} (${result.contentLength} chars)`);
                
                const pageData = {
                    url: pageUrl,
                    pageNumber: pageNum,
                    title: result.title,
                    contentLength: result.contentLength
                };
                
                sectionResults.pages.push(pageData);
                sectionResults.totalPages++;
                results.totalWorkingUrls++;
                
                allUrls.push({
                    sectionName: sectionName,
                    url: pageUrl,
                    pageNumber: pageNum,
                    title: result.title,
                    contentLength: result.contentLength
                });
            } else {
                console.log(`    ✗ Failed: ${result.error || result.status}`);
                
                // If we hit 3 consecutive 404s, assume no more pages in this section
                if (result.status === 404) {
                    const recentPages = sectionResults.pages.slice(-3);
                    if (recentPages.length === 0 && pageNum > 3) {
                        console.log(`    Stopping section ${sectionName} after 3 consecutive 404s`);
                        break;
                    }
                }
            }
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 150));
        }
        
        results.sections[sectionName] = sectionResults;
        results.sectionsProcessed++;
        results.totalWorkingUrls++; // Count base URL
        
        console.log(`  Section ${sectionName} complete: ${sectionResults.totalPages} total pages`);
        
        // Save progress every 5 sections
        if (results.sectionsProcessed % 5 === 0) {
            await saveProgress(allUrls, results);
        }
    }
    
    await browser.close();
    await saveProgress(allUrls, results);
    
    console.log('\n=== Paginated URL Discovery Complete ===');
    console.log(`Sections processed: ${results.sectionsProcessed}`);
    console.log(`Total URLs tested: ${results.totalUrlsTested}`);
    console.log(`Total working URLs found: ${results.totalWorkingUrls}`);
    console.log(`Average pages per section: ${(results.totalWorkingUrls / results.sectionsProcessed).toFixed(1)}`);
}

async function saveProgress(allUrls, results) {
    const output = {
        timestamp: new Date().toISOString(),
        summary: {
            totalUrls: allUrls.length,
            sectionsProcessed: results.sectionsProcessed,
            totalUrlsTested: results.totalUrlsTested
        },
        sections: results.sections,
        allUrls: allUrls
    };
    
    await fs.writeFile(config.outputFile, JSON.stringify(output, null, 2));
    console.log(`\nProgress saved: ${allUrls.length} total URLs discovered`);
}

// Run the paginated URL discovery
testPaginatedUrls().catch(console.error); 