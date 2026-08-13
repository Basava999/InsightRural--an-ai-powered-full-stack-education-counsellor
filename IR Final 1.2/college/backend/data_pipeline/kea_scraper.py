import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - KEA Scraper - %(levelname)s - %(message)s')

class KEAPDFScraper:
    """
    Scrapes the official KEA website to find and download the latest KCET cutoff PDFs.
    """
    def __init__(self, download_dir: str = "../data/raw"):
        self.base_url = "https://cetonline.karnataka.gov.in/kea/"
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
    def get_latest_cutoff_links(self) -> list:
        """
        Fetches the UGCET section and extracts PDF links related to Cutoffs.
        Note: The actual KEA website structure changes often. This targets the typical UGCET page.
        """
        # Targeting the typical URL structure for UGCET admissions
        target_url = "https://cetonline.karnataka.gov.in/kea/ugcet2024"
        
        logging.info(f"Fetching KEA URL: {target_url}")
        
        try:
            # Add a user-agent to bypass basic blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(target_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = []
            
            # Look for all anchor tags with href ending in .pdf and containing 'cutoff'
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text().lower()
                
                # Check if it's a PDF and relates to cutoffs
                if href.lower().endswith('.pdf') and ('cutoff' in text or 'cut off' in text or 'cutoff' in href.lower()):
                    full_url = urljoin(target_url, href)
                    
                    # We want Engineering cutoffs specifically (often designated 'engg' or 'gen')
                    category = "Engineering" if "engg" in text or "gen" in text else "Other"
                    
                    pdf_links.append({
                        "title": a_tag.get_text(strip=True),
                        "url": full_url,
                        "category": category
                    })
            
            return pdf_links
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch KEA page: {e}")
            return []

    def download_pdfs(self, links: list) -> list:
        """Downloads the provided list of PDFs to the raw data directory."""
        downloaded_files = []
        
        for link in links:
            url = link["url"]
            # Extract a safe filename
            filename = url.split('/')[-1]
            # If filename is generic, use title
            if len(filename) < 5:
                safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', link["title"])
                filename = f"{safe_title}.pdf"
                
            filepath = os.path.join(self.download_dir, filename)
            
            # Skip if already downloaded
            if os.path.exists(filepath):
                logging.info(f"File already exists, skipping: {filename}")
                downloaded_files.append(filepath)
                continue
                
            logging.info(f"Downloading: {filename}")
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                logging.info(f"Successfully downloaded: {filename}")
                downloaded_files.append(filepath)
            except Exception as e:
                logging.error(f"Failed to download {url}: {e}")
                
        return downloaded_files

if __name__ == "__main__":
    scraper = KEAPDFScraper()
    links = scraper.get_latest_cutoff_links()
    
    if not links:
        logging.info("No cutoff links found or page unreachable. We may need to use a sample PDF for parsing.")
    else:
        logging.info(f"Found {len(links)} cutoff PDFs.")
        scraper.download_pdfs(links)
