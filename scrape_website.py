import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
from urllib import robotparser
from playwright.sync_api import sync_playwright
from icecream import ic
import json



class WebScraper:
    def __init__(self, base_url, delay=1):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.delay = delay  # Time to wait between requests
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MyWebScraper/1.0)"
        }

        # Setup robots.txt parser
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url(urljoin(base_url, "/robots.txt"))
        try:
            self.rp.read()
        except:
            print("Could not read robots.txt")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed_url = urlparse(url)
            base_domain = urlparse(self.base_url).netloc
            return parsed_url.netloc == base_domain
        except:
            return False

    def get_links(self, soup, current_url):
        """Extract all links from a page"""
        links = set()
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                absolute_url = urljoin(current_url, href)
                if self.is_valid_url(absolute_url):
                    links.add(absolute_url)
        return links

    def save_page(self, url, content):
        """Save the scraped content to a file"""
        try:
            # Create directory structure based on URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            if not path_parts[0]:
                path_parts = ['index']
            
            # Create the directory
            save_dir = Path('scraped_site') / parsed_url.netloc / '/'.join(path_parts[:-1])
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save content and links separately
            content_file = save_dir / f"{path_parts[-1] or 'index'}.txt"
            links_file = save_dir / f"{path_parts[-1] or 'index'}_document_links.json"
            
            # Save main content
            content_file.write_text(content['content'], encoding='utf-8')
            
            # Save document links
            links_file.write_text(
                json.dumps(content['document_links'], 
                          indent=2, 
                          ensure_ascii=False),
                encoding='utf-8'
            )
            
            print(f"\n✓ Saved page content and links to {save_dir}")
            
        except Exception as e:
            print(f"✗ Error saving page {url}: {str(e)}")

    def scrape(self):
        """Main scraping method"""
        urls_to_visit = {self.base_url}

        while urls_to_visit:
            url = urls_to_visit.pop()

            if url in self.visited_urls:
                continue

            print(f"Scraping: {url}")

            try:
                # Navigate and wait for content
                self.page.goto(url, timeout=60000)
                self.page.wait_for_load_state('networkidle', timeout=60000)
                self.page.wait_for_timeout(5000)

                # Get the main page content
                content = self.page.evaluate('''() => {
                    const elements = document.querySelectorAll('script, style');
                    elements.forEach(el => el.remove());
                    return document.body.innerText;
                }''')

                # Extract document links
                document_links = self.page.evaluate('''() => {
                    const fileExtensions = ['.xlsx', '.xls', '.pdf', '.doc', '.docx'];
                    return Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => fileExtensions.some(ext => a.href.toLowerCase().endsWith(ext)))
                        .map(a => ({
                            text: a.innerText.trim(),
                            url: a.href,
                            type: a.href.split('.').pop().toLowerCase()
                        }))
                        .filter(link => link.text);
                }''')

                if document_links:
                    print(f"\nFound {len(document_links)} documents:")
                    for link in document_links:
                        try:
                            # Create directory for the file type if it doesn't exist
                            file_dir = Path('downloaded_files') / link['type']
                            file_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Clean filename
                            clean_filename = "".join(c for c in link['text'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            file_path = file_dir / f"{clean_filename}.{link['type']}"
                            
                            # Download only if file doesn't exist
                            if not file_path.exists():
                                print(f"\nDownloading: {link['text']}")
                                response = requests.get(link['url'], timeout=30)
                                if response.status_code == 200:
                                    file_path.write_bytes(response.content)
                                    print(f"✓ Saved to: {file_path}")
                                else:
                                    print(f"✗ Failed to download: HTTP {response.status_code}")
                            else:
                                print(f"• Skipped (already exists): {file_path}")
                                
                        except Exception as e:
                            print(f"✗ Error downloading {link['url']}: {str(e)}")
                            continue

                # Save the webpage content and document links
                self.save_page(url, {
                    'content': content,
                    'document_links': document_links
                })

                # Find new links for crawling
                new_links = self.page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                        .filter(href => href.startsWith('http'));
                }''')
                urls_to_visit.update(set(new_links) - self.visited_urls)

                self.visited_urls.add(url)

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

        # Clean up
        self.browser.close()
        self.playwright.stop()


if __name__ == "__main__":
    # Example usage
    scraper = WebScraper("https://palvelut.datahub.fi/en/kehitys-ja-yhteistyo/kehitystyoryhma")
    scraper.scrape()
