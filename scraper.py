import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

class ElectricityCutScraper:
    """
    Scrapes electricity cut information from ERMZapad website.

    The website lists planned electricity cuts in PDF documents.
    Each day has its own PDF file with the schedule.
    """

    def __init__(self):
        self.base_url = "https://info.ermzapad.bg"
        self.cuts_url = f"{self.base_url}/webint/vok/avplan.php?PLAN=FYI"
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self):
        """
        Fetches the main page with the list of planned cuts.

        The website loads data via AJAX POST request to avplan.php
        with action=showpdf parameter.

        Returns:
            BeautifulSoup object: Parsed HTML content
        """
        ajax_url = f"{self.base_url}/webint/vok/avplan.php"
        print(f"Fetching data via AJAX: {ajax_url}")

        # Make the same AJAX POST request that the JavaScript does
        response = self.session.post(ajax_url, data={'action': 'showpdf'})
        response.raise_for_status()  # Raise error if request failed
        return BeautifulSoup(response.content, 'html.parser')

    def extract_document_list(self, soup):
        """
        Extracts the list of PDF documents from the page.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            list: List of dictionaries containing document info
                  [{'doc_id': '1480', 'title': '...', 'date': '17.11.2025'}]
        """
        documents = []

        # Find the ordered list containing the documents
        list_items = soup.find_all('li', class_='list-group-item')

        for item in list_items:
            # Extract the link with document ID
            link = item.find('a')
            if not link:
                continue

            # Extract document ID from href="javascript:previewdoc(1480);"
            href = link.get('href', '')
            doc_id_match = re.search(r'previewdoc\((\d+)\)', href)
            if not doc_id_match:
                continue

            doc_id = doc_id_match.group(1)
            title = link.get_text(strip=True)

            # Extract date from badge
            badge = item.find('span', class_='badge')
            date_str = badge.get_text(strip=True) if badge else None

            documents.append({
                'doc_id': doc_id,
                'title': title,
                'date': date_str
            })

        return documents

    def download_pdf(self, doc_id, output_path):
        """
        Downloads a PDF document.

        The website uses POST request to avplan.php with action=showdocid
        to retrieve the PDF content.

        Args:
            doc_id: Document ID to download
            output_path: Path where to save the PDF file

        Returns:
            bool: True if successful, False otherwise
        """
        ajax_url = f"{self.base_url}/webint/vok/avplan.php"

        try:
            print(f"Downloading PDF ID: {doc_id}")
            # Make POST request with document ID
            response = self.session.post(
                ajax_url,
                data={'action': 'showdocid', 'doc_id': doc_id}
            )
            response.raise_for_status()

            # Save the PDF content
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"Saved PDF to: {output_path}")
            return True
        except Exception as e:
            print(f"Error downloading PDF {doc_id}: {e}")
            return False

    def get_latest_cuts(self, days=7):
        """
        Gets information about planned cuts for the next N days.

        Args:
            days: Number of days to retrieve (default: 7)

        Returns:
            list: List of documents for the specified period
        """
        soup = self.fetch_page()
        all_docs = self.extract_document_list(soup)

        # Return only the most recent documents (they're ordered by date)
        return all_docs[:days]


def main():
    """
    Main function to demonstrate the scraper.
    """
    print("=" * 50)
    print("Electricity Cut Scraper - ERMZapad")
    print("=" * 50)

    scraper = ElectricityCutScraper()

    # Get the latest cuts
    cuts = scraper.get_latest_cuts(days=3)

    print(f"\nFound {len(cuts)} scheduled cut announcements:")
    print("-" * 50)

    for i, doc in enumerate(cuts, 1):
        print(f"{i}. Date: {doc['date']}")
        print(f"   Title: {doc['title']}")
        print(f"   Document ID: {doc['doc_id']}")
        print()

    # Download the latest PDF as example
    if cuts:
        latest = cuts[0]
        output_file = f"cuts_{latest['date'].replace('.', '-')}.pdf"
        print(f"Downloading latest document...")
        scraper.download_pdf(latest['doc_id'], output_file)


if __name__ == "__main__":
    main()
