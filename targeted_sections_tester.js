const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// Configuration
const config = {
    baseUrl: 'https://0002n8y.wcomhost.com/website/',
    outputFile: 'targeted_sections_results.json',
    maxPagesToTest: 30,
    // Known sections with confirmed working pages
    knownSections: [
        'History1',
        'History2', 
        'everyplayer',
        'playerawards',
        'season2022' // from your earlier examples
    ]
};

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
            }
        }
        return { success: false, status: response ? response.status() : 'No response' };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function testTargetedSections() {
    console.log('Testing targeted sections with known working pages...');
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    const foundSections = [];
    const allUrls = [];
    const results = {
        sectionsWithPages: 0,
        totalPagesFound: 0,
        sectionsProcessed: 0
    };
    
    console.log(`Testing ${config.knownSections.length} known sections...`);
    
    for (const sectionName of config.knownSections) {
        console.log(`\n=== Testing Section: ${sectionName} ===`);
        
        const sectionData = {
            sectionName: sectionName,
            baseUrl: `${config.baseUrl}${sectionName}/`,
            pages: [],
            totalPages: 0
        };
        
        // First test the base directory URL
        console.log(`  Testing base: ${sectionData.baseUrl}`);
        const baseResult = await testUrl(page, sectionData.baseUrl);
        
        if (baseResult.success) {
            console.log(`  ✓ Base URL works: ${baseResult.title} (${baseResult.contentLength} chars)`);
            sectionData.pages.push({
                url: sectionData.baseUrl,
                pageNumber: 0,
                title: baseResult.title,
                contentLength: baseResult.contentLength
            });
            allUrls.push({
                sectionName: sectionName,
                url: sectionData.baseUrl,
                pageNumber: 0,
                title: baseResult.title,
                contentLength: baseResult.contentLength
            });
            sectionData.totalPages++;
        } else {
            console.log(`  ✗ Base URL failed: ${baseResult.error || baseResult.status}`);
        }
        
        let consecutiveFailures = 0;
        let foundAnyPages = baseResult.success;
        
        // Test paginated pages
        for (let pageNum = 1; pageNum <= config.maxPagesToTest; pageNum++) {
            const pageUrl = `${config.baseUrl}${sectionName}/page${pageNum}.html`;
            
            const result = await testUrl(page, pageUrl);
            
            if (result.success) {
                console.log(`  ✓ page${pageNum}.html: ${result.title} (${result.contentLength} chars)`);
                
                const pageData = {
                    url: pageUrl,
                    pageNumber: pageNum,
                    title: result.title,
                    contentLength: result.contentLength
                };
                
                sectionData.pages.push(pageData);
                allUrls.push({
                    sectionName: sectionName,
                    ...pageData
                });
                
                sectionData.totalPages++;
                results.totalPagesFound++;
                foundAnyPages = true;
                consecutiveFailures = 0;
            } else {
                consecutiveFailures++;
                
                // If we found some pages but then hit 5 consecutive failures, 
                // assume we've reached the end of this section
                if (foundAnyPages && consecutiveFailures >= 5) {
                    console.log(`  Stopping ${sectionName} after 5 consecutive failures`);
                    break;
                }
                
                // If we haven't found any pages and hit 8 consecutive failures,
                // assume this section doesn't have more pages
                if (!foundAnyPages && consecutiveFailures >= 8) {
                    break;
                }
            }
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        if (foundAnyPages) {
            foundSections.push(sectionData);
            results.sectionsWithPages++;
            console.log(`  ✓ Section ${sectionName}: ${sectionData.totalPages} total pages found`);
        } else {
            console.log(`  ✗ Section ${sectionName}: No pages found`);
        }
        
        results.sectionsProcessed++;
        
        // Save progress after each section
        await saveProgress(foundSections, allUrls, results);
    }
    
    await browser.close();
    await saveProgress(foundSections, allUrls, results);
    
    console.log('\n=== Targeted Sections Discovery Complete ===');
    console.log(`Sections processed: ${results.sectionsProcessed}`);
    console.log(`Sections with pages: ${results.sectionsWithPages}`);
    console.log(`Total pages found: ${results.totalPagesFound}`);
    
    // Show summary by section
    foundSections.forEach(section => {
        console.log(`  ${section.sectionName}: ${section.totalPages} pages`);
    });
}

async function saveProgress(foundSections, allUrls, results) {
    const output = {
        timestamp: new Date().toISOString(),
        summary: {
            sectionsWithPages: results.sectionsWithPages,
            totalPagesFound: results.totalPagesFound,
            sectionsProcessed: results.sectionsProcessed
        },
        sections: foundSections,
        allUrls: allUrls
    };
    
    await fs.writeFile(config.outputFile, JSON.stringify(output, null, 2));
    console.log(`\nProgress saved: ${results.totalPagesFound} pages across ${results.sectionsWithPages} sections`);
}

// Run the targeted sections discovery
testTargetedSections().catch(console.error); 