const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const LIVE_SITE = 'https://0002n8y.wcomhost.com/website/';
const LOCAL_SITE = 'http://localhost:8000/';
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 2000; // 2 seconds

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function loadPageWithRetry(page, url, attempts = RETRY_ATTEMPTS) {
  for (let i = 0; i < attempts; i++) {
    try {
      await page.goto(url, { 
        waitUntil: 'networkidle0',
        timeout: 30000 
      });
      await sleep(1000); // Wait for any dynamic content
      return true;
    } catch (error) {
      console.error(`Attempt ${i + 1} failed for ${url}:`, error.message);
      if (i < attempts - 1) {
        await sleep(RETRY_DELAY);
      }
    }
  }
  return false;
}

async function comparePages() {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  // Store comparison results
  const results = {
    missingPages: [],
    differentPages: [],
    missingImages: [],
    brokenLinks: []
  };

  // Get list of local HTML files
  const localPages = fs.readdirSync(path.join(__dirname, 'pages'))
    .filter(file => file.endsWith('.html'));

  // Compare each page
  for (const localPage of localPages) {
    const localUrl = `${LOCAL_SITE}pages/${localPage}`;
    const liveUrl = `${LIVE_SITE}${localPage}`;

    try {
      // Load local page
      const localLoaded = await loadPageWithRetry(page, localUrl);
      if (!localLoaded) {
        results.missingPages.push(localPage);
        continue;
      }

      const localContent = await page.content();
      const localImages = await page.evaluate(() => 
        Array.from(document.images).map(img => img.src)
      );

      // Load live page
      const liveLoaded = await loadPageWithRetry(page, liveUrl);
      if (!liveLoaded) {
        results.missingPages.push(localPage);
        continue;
      }

      const liveContent = await page.content();
      const liveImages = await page.evaluate(() => 
        Array.from(document.images).map(img => img.src)
      );

      // Compare content
      if (localContent !== liveContent) {
        results.differentPages.push(localPage);
      }

      // Check for missing images
      const missingImages = liveImages.filter(img => !localImages.includes(img));
      if (missingImages.length > 0) {
        results.missingImages.push({
          page: localPage,
          images: missingImages
        });
      }

      // Check for broken links
      const brokenLinks = await page.evaluate(() => {
        const links = Array.from(document.getElementsByTagName('a'));
        return links.filter(link => {
          try {
            new URL(link.href);
            return false;
          } catch {
            return true;
          }
        }).map(link => link.href);
      });

      if (brokenLinks.length > 0) {
        results.brokenLinks.push({
          page: localPage,
          links: brokenLinks
        });
      }

    } catch (error) {
      console.error(`Error comparing ${localPage}:`, error.message);
      results.missingPages.push(localPage);
    }

    // Add a small delay between pages
    await sleep(500);
  }

  // Save results
  fs.writeFileSync(
    path.join(__dirname, 'comparison_results.json'),
    JSON.stringify(results, null, 2)
  );

  await browser.close();
  return results;
}

// Run the comparison
comparePages().then(results => {
  console.log('Comparison complete! Results saved to comparison_results.json');
  console.log('\nSummary:');
  console.log(`Missing pages: ${results.missingPages.length}`);
  console.log(`Different pages: ${results.differentPages.length}`);
  console.log(`Pages with missing images: ${results.missingImages.length}`);
  console.log(`Pages with broken links: ${results.brokenLinks.length}`);
}); 