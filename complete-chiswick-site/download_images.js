const fs = require('fs');
const path = require('path');
const https = require('https');
const { promisify } = require('util');

const LIVE_SITE = 'https://0002n8y.wcomhost.com/website/';
const IMAGES_DIR = path.join(__dirname, 'assets', 'images');
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 2000; // 2 seconds

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function downloadImage(url, filePath, attempts = RETRY_ATTEMPTS) {
  for (let i = 0; i < attempts; i++) {
    try {
      return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filePath);
        https.get(url, response => {
          if (response.statusCode !== 200) {
            reject(new Error(`Failed to download ${url}: ${response.statusCode}`));
            return;
          }

          response.pipe(file);
          file.on('finish', () => {
            file.close();
            resolve();
          });
        }).on('error', err => {
          fs.unlink(filePath, () => {}); // Delete the file if download fails
          reject(err);
        });
      });
    } catch (error) {
      console.error(`Attempt ${i + 1} failed for ${url}:`, error.message);
      if (i < attempts - 1) {
        await sleep(RETRY_DELAY);
      } else {
        throw error;
      }
    }
  }
}

async function downloadMissingImages() {
  // Ensure images directory exists
  if (!fs.existsSync(IMAGES_DIR)) {
    fs.mkdirSync(IMAGES_DIR, { recursive: true });
  }

  // Read comparison results
  const results = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'comparison_results.json'), 'utf8')
  );

  // Download missing images
  const missingImages = results.missingImages.flatMap(item => 
    item.images.map(img => ({
      url: img.startsWith('http') ? img : `${LIVE_SITE}${img}`,
      path: path.join(IMAGES_DIR, path.basename(img))
    }))
  );

  console.log(`Found ${missingImages.length} missing images to download`);

  // Download images in batches of 5
  const batchSize = 5;
  for (let i = 0; i < missingImages.length; i += batchSize) {
    const batch = missingImages.slice(i, i + batchSize);
    await Promise.all(
      batch.map(async ({ url, path }) => {
        try {
          console.log(`Downloading ${url} to ${path}`);
          await downloadImage(url, path);
          console.log(`Successfully downloaded ${path}`);
        } catch (error) {
          console.error(`Failed to download ${url}:`, error.message);
        }
      })
    );
    // Add a small delay between batches
    if (i + batchSize < missingImages.length) {
      await sleep(1000);
    }
  }

  console.log('Download complete!');
}

// Run the download
downloadMissingImages().catch(console.error); 