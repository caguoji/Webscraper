## Creating a data pipeline for scraped web data and images

### Steps
1. Use Scrapy Playwright to scrape Javascript enabled website.
2. Scrape both product information and image for every item.
3. Save product information as json file.
4. Clear background of all images and resize image size.
5. Upload scraped images to Amazon S3 bucket.
6. Upload scraped data to Amazon RDS Instance

### Output
1. Scrapy file which scrapes data, saves original and resized image to s3 bucket.


### Issues
1. Configuring Scrapy Playwright to download 2 versions of the same image with 1 scrape
2. Scraping pricing information from javascript enabled API call
3. Configuring scrapy data and image pipelines from source code

### Business Requirements
1. Data formatting of various fields.
2. Image size requirements for each image.
3. Image filetype requirement.

