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
        """Check if URL belongs to the same domain and is allowed by robots.txt"""
        parsed = urlparse(url)
        is_same_domain = parsed.netloc == self.domain
        is_allowed = self.rp.can_fetch(self.session.headers["User-Agent"], url)
        return is_same_domain and is_allowed

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
        """Save the page content to a file"""
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            path = "index.html"

        # Create directory structure
        save_path = Path("scraped_site") / self.domain / path
        # ic(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)

    def scrape(self):
        """Main scraping method"""
        urls_to_visit = {self.base_url}

        while urls_to_visit:
            url = urls_to_visit.pop()

            if url in self.visited_urls:
                continue

            print(f"Scraping: {url}")

            try:
                # Navigate to the page
                self.page.goto(url, timeout=60000)
                
                # Handle cookie banner - look for common cookie accept buttons
                try:
                    # Wait for cookie banner with longer timeout
                    self.page.wait_for_selector('button:has-text("Allow all"), button:has-text("Hyväksy")', timeout=10000)
                    # Click accept button (try both English and Finnish)
                    self.page.click('button:has-text("Accept"), button:has-text("Hyväksy")')
                    # Wait for banner to disappear
                    self.page.wait_for_timeout(2000)
                except:
                    print("No cookie banner found or already accepted")

                # Wait for the main content to load
                self.page.wait_for_load_state('networkidle', timeout=60000)
                
                # Additional wait to ensure JavaScript execution
                self.page.wait_for_timeout(5000)

                # Get the page content after cookie banner is handled
                content = self.page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract all links
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    text = a.get_text(strip=True)
                    if href and text:  # Only include links with both href and text
                        links.append({
                            'text': text,
                            'url': urljoin(url, href)
                        })

                # Save the links
                self.save_page(url, json.dumps(links, indent=2, ensure_ascii=False))
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
