"""
Website Scraper Module for Lead Enrichment

Extracts text content from company websites for personalization:
- Services page text
- About page text  
- Blog headlines

Uses requests + BeautifulSoup for simple, fast extraction.
Falls back gracefully if pages don't exist.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from time import sleep


# Common paths to try for each page type
ABOUT_PATHS = ['/about', '/about-us', '/about-us/', '/about/', '/company', '/who-we-are']
SERVICES_PATHS = ['/services', '/services/', '/what-we-do', '/our-services', '/solutions']
BLOG_PATHS = ['/blog', '/blog/', '/news', '/insights', '/articles', '/resources']

# Request settings
TIMEOUT = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def normalize_url(url):
    """Ensure URL has scheme and normalize it."""
    if not url:
        return None
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    # Remove trailing slash for consistency
    return url.rstrip('/')


def get_page(url):
    """
    Fetch a page and return BeautifulSoup object.
    Returns None if page doesn't exist or fails.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        return None
    except Exception as e:
        # Silently fail - we'll try other paths
        return None


def extract_text_content(soup, max_length=1000):
    """
    Extract meaningful text content from a page.
    Removes scripts, styles, navigation, footers, etc.
    """
    if not soup:
        return None
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
        element.decompose()
    
    # Try to find main content area
    main_content = (
        soup.find('main') or 
        soup.find('article') or 
        soup.find('div', class_=re.compile(r'content|main|body', re.I)) or
        soup.find('div', id=re.compile(r'content|main|body', re.I)) or
        soup.body
    )
    
    if not main_content:
        return None
    
    # Get text and clean it up
    text = main_content.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text if len(text) > 50 else None  # Ignore very short content


def extract_blog_headlines(soup, max_headlines=5):
    """
    Extract blog post headlines from a blog listing page.
    """
    if not soup:
        return []
    
    headlines = []
    
    # Common patterns for blog post titles
    selectors = [
        'article h2',
        'article h3',
        '.post-title',
        '.entry-title',
        '.blog-title',
        'h2.title',
        'h3.title',
        '.card-title',
        'a[href*="/blog/"] h2',
        'a[href*="/blog/"] h3',
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        for el in elements[:max_headlines]:
            text = el.get_text(strip=True)
            if text and len(text) > 10 and len(text) < 200:
                headlines.append(text)
        if headlines:
            break
    
    # Fallback: look for any h2/h3 that might be post titles
    if not headlines:
        for tag in ['h2', 'h3']:
            for el in soup.find_all(tag)[:max_headlines * 2]:
                text = el.get_text(strip=True)
                # Filter out navigation/generic headings
                if text and len(text) > 15 and len(text) < 150:
                    if not any(skip in text.lower() for skip in ['menu', 'navigation', 'contact', 'footer', 'subscribe']):
                        headlines.append(text)
            if len(headlines) >= max_headlines:
                break
    
    return headlines[:max_headlines]


def try_pages(base_url, paths):
    """
    Try multiple path variations and return first successful result.
    """
    for path in paths:
        url = urljoin(base_url + '/', path.lstrip('/'))
        soup = get_page(url)
        if soup:
            return soup, url
        sleep(0.3)  # Be polite between requests
    return None, None


def scrape_website(website_url):
    """
    Main function: Scrape a company website for personalization data.
    
    Args:
        website_url: The company's website URL (e.g., "example.com" or "https://example.com")
        
    Returns:
        dict: {
            "services": str or None,
            "about": str or None,
            "blog_headlines": list[str],
            "success": bool,
            "sources_found": list[str]
        }
    """
    result = {
        "services": None,
        "about": None,
        "blog_headlines": [],
        "success": False,
        "sources_found": []
    }
    
    base_url = normalize_url(website_url)
    if not base_url:
        return result
    
    # Try homepage first to verify site is reachable
    homepage_soup = get_page(base_url)
    if not homepage_soup:
        # Try with www prefix
        parsed = urlparse(base_url)
        if not parsed.netloc.startswith('www.'):
            alt_url = f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}"
            homepage_soup = get_page(alt_url)
            if homepage_soup:
                base_url = alt_url
    
    if not homepage_soup:
        return result  # Site unreachable
    
    # 1. Try to get About page
    about_soup, about_url = try_pages(base_url, ABOUT_PATHS)
    if about_soup:
        about_text = extract_text_content(about_soup)
        if about_text:
            result["about"] = about_text
            result["sources_found"].append("about")
    
    # 2. Try to get Services page
    services_soup, services_url = try_pages(base_url, SERVICES_PATHS)
    if services_soup:
        services_text = extract_text_content(services_soup)
        if services_text:
            result["services"] = services_text
            result["sources_found"].append("services")
    
    # 3. Try to get Blog headlines
    blog_soup, blog_url = try_pages(base_url, BLOG_PATHS)
    if blog_soup:
        headlines = extract_blog_headlines(blog_soup)
        if headlines:
            result["blog_headlines"] = headlines
            result["sources_found"].append("blog")
    
    # If we got nothing from subpages, try to extract from homepage
    if not result["sources_found"]:
        homepage_text = extract_text_content(homepage_soup, max_length=1500)
        if homepage_text:
            result["about"] = homepage_text
            result["sources_found"].append("homepage")
    
    result["success"] = len(result["sources_found"]) > 0
    
    return result


# For standalone testing
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python website_scraper.py <website_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Scraping: {url}")
    
    result = scrape_website(url)
    print(json.dumps(result, indent=2))
