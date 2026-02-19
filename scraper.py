import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# scrapes jobs from indeed
# indeed blocks web scrapers but still want to include
class IndeedScraper:
    def __init__(self):
        self.base_url = "https://www.indeed.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_jobs(self, query: str, location: str = "", max_results: int = 20) -> List[dict]:
        jobs = []

        # build search url
        search_url = f"{self.base_url}/jobs"
        params = {
            'q': query,
            'l': location,
            'limit': 50
        }

        try:
            logger.info(f"Searching Indeed for '{query}' in '{location}'")
            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # find job cards
            job_cards = soup.find_all("div", class_="job_seen_beacon")

            if not job_cards:
                job_cards = soup.find_all("td", class_="resultContent")
            
            logger.info(f"Found {len(job_cards)} job cards")

            for card in job_cards[:max_results]:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
                time.sleep(0.5)
            logger.info(f"Successfully parsed {len(jobs)} jobs")
            return jobs
        
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []
        
    # parse individual job cards
    def _parse_job_card(self, card) -> Optional[dict]:
        try:
            # extract title and url
            title_elem = card.find("h2", class_="jobTitle")
            if not title_elem:
                return None

            title_link = title_elem.find("a")
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            job_id = title_link.get("data-jk") or title_link.get("id", "").replace("job_", "")
            url = f"{self.base_url}/viewjob?jk={job_id}" if job_id else title_link.get("href", "")

            # extract company
            company_elem = card.find("span", {"data-testid": "company-name"})
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"

            # extract location
            location_elem = card.find("span", {"data-testid": "text-location"})
            location = location_elem.get_text(strip=True) if location_elem else None

            # extract a short desc
            snippet_elem = card.find("div", class_="job-snippet")
            description = snippet_elem.get_text(strip=True) if snippet_elem else None

            return {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "description": description,
                "source": "Indeed"
            }
        
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None

# simple scraper that just demonstrates the concept
class MockScraper:
    def search_jobs(self, query: str, location: str = "", max_results: int = 20) -> List[Dict]:
        return [
            {
                "title": f"{query} - Position 1",
                "company": "Tech Corp",
                "location": location or "Remote",
                "url": f"https://example.com/job1",
                "description": f"Great opportunity for {query} role",
                "source": "mock"
            },
            {
                "title": f"{query} - Position 2",
                "company": "StartupXYZ",
                "location": location or "San Francisco, CA",
                "url": f"https://example.com/job2",
                "description": f"Exciting {query} position at a growing startup",
                "source": "mock"
            },
            {
                "title": f"Senior {query}",
                "company": "Big Tech Inc",
                "location": location or "New York, NY",
                "url": f"https://example.com/job3",
                "description": f"Senior level {query} role with competitive pay",
                "source": "mock"
            }
        ]


