#!/usr/bin/env python3
"""
Electricity Cut Notifier - Main Application

This script:
1. Scrapes the ERMZapad website for planned electricity cuts
2. Downloads PDF documents
3. Extracts and filters cuts by city/location
4. Sends email notifications to subscribed users
"""

import os
import json
from scraper import ElectricityCutScraper
from pdf_parser import PDFCutParser
from email_notifier import EmailNotifier
import traceback


class CutNotifier:
    """
    Main application class for monitoring and notifying about electricity cuts.
    """

    def __init__(self, config_file='config.json'):
        """
        Initialize the notifier with configuration.

        Args:
            config_file: Path to JSON configuration file
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.validate_config()
        self.scraper = ElectricityCutScraper()

    def load_config(self):
        """
        Loads configuration from JSON file and environment variables.

        Environment variables (for GitHub Actions):
        - SENDER_EMAIL: Email address to send from
        - SENDER_PASSWORD: Email password
        - EMAIL_RECIPIENTS: Comma-separated list of recipients

        Config format:
        {
            "monitored_cities": ["СОФИЯ", "ПЕРНИК", "БЛАГОЕВГРАД"],
            "pdf_cache_dir": "./pdfs",
            "check_days_ahead": 3
        }

        Returns:
            dict: Configuration dictionary
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"❌ Configuration file '{self.config_file}' not found!\n"
                f"   Create it from the example: cp config.example.json config.json\n"
                f"   See README.md for configuration instructions."
            )

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"❌ Invalid JSON in '{self.config_file}':\n"
                f"   {str(e)}\n"
                f"   Check for syntax errors (missing commas, quotes, etc.)"
            )

        # Override with environment variables (for GitHub Actions)
        config['sender_email'] = os.getenv('SENDER_EMAIL', '').strip()
        config['sender_password'] = os.getenv('SENDER_PASSWORD', '').strip()

        # Parse comma-separated recipients from env var
        recipients_env = os.getenv('EMAIL_RECIPIENTS', '').strip()
        if recipients_env:
            config['email_recipients'] = [email.strip() for email in recipients_env.split(',') if email.strip()]
        elif 'email_recipients' not in config:
            config['email_recipients'] = []

        return config

    def validate_config(self):
        """
        Validates configuration and fails fast if something is wrong.

        This ensures errors are caught early in the GitHub Actions pipeline.
        """
        errors = []

        # Check required fields in config.json
        if not self.config.get('monitored_cities'):
            errors.append("❌ 'monitored_cities' is missing or empty in config.json")
        elif not isinstance(self.config['monitored_cities'], list):
            errors.append("❌ 'monitored_cities' must be a list")
        elif len(self.config['monitored_cities']) == 0:
            errors.append("❌ 'monitored_cities' list is empty - add at least one city")

        if not self.config.get('smtp_server'):
            errors.append("❌ 'smtp_server' is missing in config.json")

        if not self.config.get('smtp_port'):
            errors.append("❌ 'smtp_port' is missing in config.json")
        elif not isinstance(self.config['smtp_port'], int):
            errors.append(f"❌ 'smtp_port' must be a number, got: {type(self.config['smtp_port']).__name__}")

        # Check environment variables (GitHub Secrets)
        if not self.config.get('sender_email'):
            errors.append("❌ SENDER_EMAIL environment variable is not set (check GitHub Secrets)")

        if not self.config.get('sender_password'):
            errors.append("❌ SENDER_PASSWORD environment variable is not set (check GitHub Secrets)")

        if not self.config.get('email_recipients'):
            errors.append("❌ EMAIL_RECIPIENTS environment variable is not set (check GitHub Secrets)")
        elif not isinstance(self.config['email_recipients'], list):
            errors.append("❌ EMAIL_RECIPIENTS must be a comma-separated list")
        elif len(self.config['email_recipients']) == 0:
            errors.append("❌ EMAIL_RECIPIENTS is empty - add at least one recipient")

        # Validate email format (basic check)
        sender = self.config.get('sender_email', '')
        if sender and '@' not in sender:
            errors.append(f"❌ SENDER_EMAIL appears invalid: '{sender}'")

        for recipient in self.config.get('email_recipients', []):
            if '@' not in recipient:
                errors.append(f"❌ EMAIL_RECIPIENTS contains invalid email: '{recipient}'")

        # Validate SMTP port
        smtp_port = self.config.get('smtp_port')
        if smtp_port and smtp_port not in [25, 465, 587, 2525]:
            print(f"⚠️  Warning: Unusual SMTP port {smtp_port}. Common ports: 465 (SSL), 587 (TLS)")

        # If there are errors, print them and fail
        if errors:
            print("\n" + "=" * 70)
            print("КОНФИГУРАЦИОННА ГРЕШКА / CONFIGURATION ERROR")
            print("=" * 70)
            print("\nПроблеми с конфигурацията / Configuration issues:\n")
            for error in errors:
                print(f"  {error}")

            print("\n" + "-" * 70)
            print("Как да поправите / How to fix:")
            print("-" * 70)
            print("1. Проверете config.json за градове и SMTP настройки")
            print("   Check config.json for cities and SMTP settings")
            print("\n2. Проверете GitHub Secrets (Settings → Secrets → Actions):")
            print("   Check GitHub Secrets (Settings → Secrets → Actions):")
            print("   - SENDER_EMAIL")
            print("   - SENDER_PASSWORD")
            print("   - EMAIL_RECIPIENTS")
            print("\n3. Вижте README.md за детайли")
            print("   See README.md for details")
            print("=" * 70 + "\n")

            raise ValueError(f"Configuration validation failed with {len(errors)} error(s)")

        # Success message with debugging info
        print("✅ Configuration validated successfully")
        print(f"   - Monitoring {len(self.config['monitored_cities'])} city/cities: {', '.join(self.config['monitored_cities'])}")
        print(f"   - Sender email: {self.config['sender_email']}")
        print(f"   - Password length: {len(self.config['sender_password'])} characters")
        print(f"   - Will notify {len(self.config['email_recipients'])} recipient(s): {', '.join(self.config['email_recipients'])}")
        print(f"   - Using SMTP: {self.config['smtp_server']}:{self.config['smtp_port']}")
        print(f"   - Connection type: {'SSL' if self.config['smtp_port'] == 465 else 'TLS'}\n")

    def save_config(self, config=None):
        """
        Saves configuration to JSON file.

        Args:
            config: Configuration dict to save (uses self.config if None)
        """
        if config is None:
            config = self.config

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def ensure_cache_dir(self):
        """
        Creates the PDF cache directory if it doesn't exist.
        """
        cache_dir = self.config['pdf_cache_dir']
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            print(f"Created cache directory: {cache_dir}")

    def fetch_latest_cuts(self):
        """
        Fetches the latest cut announcements from the website.

        Returns:
            list: List of document metadata
        """
        days = self.config.get('check_days_ahead', 3)
        print(f"\nFetching planned cuts for next {days} days...")
        return self.scraper.get_latest_cuts(days=days)

    def download_and_parse_pdf(self, doc):
        """
        Downloads a PDF and parses its contents.

        Args:
            doc: Document metadata dict with 'doc_id' and 'date'

        Returns:
            tuple: (pdf_path, list of cut entries)
        """
        self.ensure_cache_dir()

        # Generate filename
        date_clean = doc['date'].replace('.', '-')
        pdf_path = os.path.join(
            self.config['pdf_cache_dir'],
            f"cuts_{date_clean}.pdf"
        )

        # Download if not cached
        if not os.path.exists(pdf_path):
            print(f"Downloading PDF for {doc['date']}...")
            success = self.scraper.download_pdf(doc['doc_id'], pdf_path)
            if not success:
                return None, []
        else:
            print(f"Using cached PDF for {doc['date']}")

        # Parse the PDF
        parser = PDFCutParser(pdf_path)
        cuts = parser.extract_cut_details()

        return pdf_path, cuts

    def filter_cuts_by_city(self, cuts, cities):
        """
        Filters electricity cuts to only include specified cities.

        Args:
            cuts: List of cut entry dicts
            cities: List of city names to match (case-insensitive)

        Returns:
            list: Filtered cuts that match the specified cities
        """
        if not cities:
            return cuts

        filtered = []
        cities_upper = [city.upper() for city in cities]

        for cut in cuts:
            location = cut['location'].upper()

            # Check if any of the monitored cities appear in the location
            for city in cities_upper:
                if city in location:
                    filtered.append(cut)
                    break

        return filtered

    def check_for_cuts(self):
        """
        Main method to check for electricity cuts in monitored cities.

        Returns:
            dict: Results with format:
                  {
                      'date': [list of cuts],
                      ...
                  }
        """
        print("=" * 70)
        print("Electricity Cut Notifier")
        print("=" * 70)

        monitored_cities = self.config['monitored_cities']
        print(f"Monitoring cities: {', '.join(monitored_cities)}")

        # Fetch latest documents
        documents = self.fetch_latest_cuts()
        print(f"Found {len(documents)} documents to check\n")

        results = {}

        # Process each document
        for doc in documents:
            print(f"\nProcessing: {doc['title']}")
            print("-" * 70)

            pdf_path, cuts = self.download_and_parse_pdf(doc)

            if not cuts:
                print(f"  No cuts found in document")
                continue

            print(f"  Total cuts in document: {len(cuts)}")

            # Filter by monitored cities
            filtered_cuts = self.filter_cuts_by_city(cuts, monitored_cities)

            if filtered_cuts:
                results[doc['date']] = filtered_cuts
                print(f"  ALERT: {len(filtered_cuts)} cut(s) affect your monitored cities!")

                for cut in filtered_cuts:
                    print(f"    - {cut['location']}: "
                          f"{cut['time_start']} - {cut['time_end']}")
            else:
                print(f"  No cuts affect your monitored cities")

        return results

    def format_notification_message(self, results):
        """
        Formats the results into a human-readable message in Bulgarian.

        Args:
            results: Dict of cuts organized by date

        Returns:
            str: Formatted message in Bulgarian
        """
        if not results:
            return "Няма планирани прекъсвания на електрозахранването за вашите населени места."

        lines = ["ПЛАНИРАНИ ПРЕКЪСВАНИЯ НА ТОКА - ИЗВЕСТИЕ", "=" * 70, ""]

        for date, cuts in sorted(results.items()):
            lines.append(f"Дата: {date}")
            lines.append("-" * 70)

            for cut in cuts:
                lines.append(f"Населено място: {cut['location']}")
                lines.append(f"Област: {cut['region']}")
                lines.append(f"Община: {cut['municipality']}")
                lines.append(f"Време: {cut['time_start']} - {cut['time_end']}")
                lines.append("")

        lines.append("=" * 70)
        lines.append("Източник: https://info.ermzapad.bg/webint/vok/avplan.php?PLAN=FYI")

        return "\n".join(lines)


def main():
    """
    Main entry point with error handling.
    """
    try:
        notifier = CutNotifier()

        # Check for cuts
        results = notifier.check_for_cuts()

        # Display results
        print("\n" + "=" * 70)
        print("РЕЗЮМЕ")
        print("=" * 70)

        message = notifier.format_notification_message(results)
        print(message)

        # Send email notifications
        if results and notifier.config.get('email_recipients'):
            recipients = notifier.config['email_recipients']
            print(f"\nИзпращане на имейл известие до {len(recipients)} получател(и)...")

            email_notifier = EmailNotifier(
                smtp_server=notifier.config.get('smtp_server', 'smtp.gmail.com'),
                smtp_port=notifier.config.get('smtp_port', 587),
                sender_email=notifier.config.get('sender_email', ''),
                sender_password=notifier.config.get('sender_password', '')
            )

            subject = f"Известие за прекъсване на тока - {len(results)} дат(и) засегнат(и)"
            email_notifier.send_notification(recipients, subject, message)
        elif results:
            print("\nНяма конфигурирани получатели на имейл. Добавете ги в config.json за да получавате известия.")
        else:
            print("\nНе са намерени прекъсвания - не е необходимо известие.")

    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()

        print("\n" + "=" * 70)
        print("ГРЕШКА / ERROR")
        print("=" * 70)
        print(f"Възникна грешка: {error_msg}")
        print("\nПълни детайли:")
        print(error_trace)
        print("\n" + "=" * 70)
        print("GitHub Actions will send you a notification about this failure.")
        print("Check the Actions tab in your repository for full logs.")
        print("=" * 70)

        # Re-raise to ensure GitHub Actions marks the run as failed
        raise


if __name__ == "__main__":
    main()
