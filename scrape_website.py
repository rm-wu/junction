import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path
from urllib import robotparser
from playwright.sync_api import sync_playwright



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
        self.browser = self.playwright.chromium.launch()
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
                # Respect crawl delay
                time.sleep(self.delay)

                # Use Playwright instead of requests
                self.page.goto(url)
                self.page.wait_for_load_state('networkidle')
                content = self.page.content()

                self.visited_urls.add(url)

                # Parse the page content
                soup = BeautifulSoup(content, "html.parser")

                # Save the page
                self.save_page(url, content)

                # Find new links
                new_links = self.get_links(soup, url)
                urls_to_visit.update(new_links - self.visited_urls)

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

    def __del__(self):
        # Clean up Playwright resources
        self.browser.close()
        self.playwright.stop()


if __name__ == "__main__":
    # Example usage
    scraper = WebScraper("https://palvelut.datahub.fi/en/kehitys-ja-yhteistyo/kehitystyoryhma")
    scraper.scrape()