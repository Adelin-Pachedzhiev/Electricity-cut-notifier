import PyPDF2
import re
from datetime import datetime


class PDFCutParser:
    """
    Parses electricity cut PDF documents to extract location and time information.
    """

    def __init__(self, pdf_path):
        """
        Initialize parser with a PDF file path.

        Args:
            pdf_path: Path to the PDF file to parse
        """
        self.pdf_path = pdf_path
        self.text = None

    def extract_text(self):
        """
        Extracts all text content from the PDF.

        Returns:
            str: Extracted text from all pages
        """
        text_content = []

        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                print(f"Reading {num_pages} pages from PDF...")

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())

            self.text = '\n'.join(text_content)
            return self.text

        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    def search_city(self, city_name):
        """
        Searches for a specific city in the PDF text.

        Args:
            city_name: Name of the city to search for (e.g., "София", "Перник")

        Returns:
            list: List of dictionaries with match details
                  [{'text': '...', 'line_number': 10}]
        """
        if not self.text:
            self.extract_text()

        if not self.text:
            return []

        matches = []
        lines = self.text.split('\n')

        # Search case-insensitive
        pattern = re.compile(re.escape(city_name), re.IGNORECASE)

        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                matches.append({
                    'line_number': i,
                    'text': line.strip()
                })

        return matches

    def extract_cut_details(self):
        """
        Extracts structured information about planned cuts.

        Parses the Bulgarian electricity cut PDF format which contains:
        - Region (област)
        - Municipality (община)
        - Location/city (населено място)
        - Date and time intervals (DD.MM.YYYY HH:MM)

        Returns:
            list: List of cut entries with structured details
                  [{'location': 'СОФИЯ', 'start': '08:30', 'end': '16:30',
                    'date_start': '18.11.2025', 'date_end': '18.11.2025',
                    'region': 'СОФИЯ', 'municipality': 'СОФИЯ'}]
        """
        if not self.text:
            self.extract_text()

        if not self.text:
            return []

        cuts = []
        lines = self.text.split('\n')

        # Pattern to match cut entries:
        # "Част от LOCATION DD.MM.YYYY HH:MM DD.MM.YYYY HH:MM"
        cut_pattern = re.compile(
            r'Част от (.+?)\s+'  # Location name
            r'(\d{2}\.\d{2}\.\d{4})\s+'  # Start date
            r'(\d{2}:\d{2})\s+'  # Start time
            r'(\d{2}\.\d{2}\.\d{4})\s+'  # End date
            r'(\d{2}:\d{2})'  # End time
        )

        # Track current region and municipality as we parse
        current_region = None
        current_municipality = None

        region_pattern = re.compile(r'област (.+?) Част от')
        municipality_pattern = re.compile(r'община (.+?) За индивидуална')

        for line in lines:
            # Check for region
            region_match = region_pattern.search(line)
            if region_match:
                current_region = region_match.group(1).strip()

            # Check for municipality
            muni_match = municipality_pattern.search(line)
            if muni_match:
                current_municipality = muni_match.group(1).strip()

            # Check for cut entry
            cut_match = cut_pattern.search(line)
            if cut_match:
                location = cut_match.group(1).strip()
                date_start = cut_match.group(2)
                time_start = cut_match.group(3)
                date_end = cut_match.group(4)
                time_end = cut_match.group(5)

                cuts.append({
                    'location': location,
                    'date_start': date_start,
                    'time_start': time_start,
                    'date_end': date_end,
                    'time_end': time_end,
                    'region': current_region,
                    'municipality': current_municipality,
                    'full_line': line.strip()
                })

        return cuts

    def get_all_text(self):
        """
        Returns the full extracted text.

        Returns:
            str: Complete text from PDF
        """
        if not self.text:
            self.extract_text()
        return self.text


def main():
    """
    Demo function to test PDF parsing.
    """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_parser.py <pdf_file> [city_name]")
        print("\nExample:")
        print("  python pdf_parser.py cuts_18-11-2025.pdf София")
        return

    pdf_file = sys.argv[1]
    city = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Parsing PDF: {pdf_file}")
    print("=" * 50)

    parser = PDFCutParser(pdf_file)

    if city:
        # Search for specific city
        print(f"\nSearching for: {city}")
        print("-" * 50)
        matches = parser.search_city(city)

        if matches:
            print(f"Found {len(matches)} mention(s) of '{city}':\n")
            for match in matches:
                print(f"Line {match['line_number']}: {match['text']}")
                print()
        else:
            print(f"No mentions of '{city}' found in the document.")
    else:
        # Extract all cuts
        print("\nExtracting all planned cuts...")
        print("-" * 50)
        cuts = parser.extract_cut_details()

        if cuts:
            print(f"Found {len(cuts)} planned cut entries:\n")
            for i, cut in enumerate(cuts[:10], 1):  # Show first 10
                print(f"{i}. Location: {cut['location']}")
                print(f"   Region: {cut['region']}")
                print(f"   Municipality: {cut['municipality']}")
                print(f"   Time: {cut['date_start']} {cut['time_start']} - "
                      f"{cut['date_end']} {cut['time_end']}")
                print()

            if len(cuts) > 10:
                print(f"... and {len(cuts) - 10} more entries")
        else:
            print("No cut entries found.")


if __name__ == "__main__":
    main()
