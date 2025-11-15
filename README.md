# Electricity Cut Notifier

An automated system that scrapes electricity cut announcements from the ERMZapad website and sends email notifications when your city is affected.

## Features

- Scrapes planned electricity cuts from https://info.ermzapad.bg
- Downloads and parses PDF documents containing cut schedules
- Filters cuts by specified cities/locations
- Sends email notifications to subscribed users
- Supports automated scheduling (cron or continuous mode)
- Caches PDFs to minimize network requests

## How It Works

The ERMZapad website publishes daily PDFs with planned electricity cuts for the western regions of Bulgaria. This application:

1. **Scrapes the website** using AJAX requests (similar to what the website's JavaScript does)
2. **Downloads PDFs** for the next few days
3. **Extracts text** from PDFs and parses location, time, and date information
4. **Filters** the cuts to only show cities you're monitoring
5. **Sends email notifications** when cuts are found

## Installation

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to customize the application:

```json
{
  "monitored_cities": ["СОФИЯ", "ПЕРНИК", "БЛАГОЕВГРАД"],
  "pdf_cache_dir": "./pdfs",
  "email_recipients": ["user1@example.com", "user2@example.com"],
  "check_days_ahead": 3,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password"
}
```

### Configuration Options

- **monitored_cities**: List of city names to monitor (in Bulgarian, uppercase)
- **pdf_cache_dir**: Directory to cache downloaded PDFs
- **email_recipients**: List of email addresses to notify
- **check_days_ahead**: How many days ahead to check
- **smtp_server**: SMTP server for sending emails
- **smtp_port**: SMTP port (587 for TLS)
- **sender_email**: Your email address
- **sender_password**: Your email password or app-specific password

### Email Setup (Gmail)

If using Gmail, you need to create an **App Password**:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll to "App passwords" at the bottom
4. Generate a new app password for "Mail"
5. Use this password in `config.json`

See: https://support.google.com/accounts/answer/185833

## Usage

### Run Once

Check for cuts and display results:

```bash
python main.py
```

### Test Email Configuration

Test your email settings:

```bash
python email_notifier.py
```

Follow the prompts to enter your SMTP configuration and send a test email.

### Parse a Specific PDF

Extract cuts from a downloaded PDF:

```bash
python pdf_parser.py pdfs/cuts_18-11-2025.pdf
```

Search for a specific city:

```bash
python pdf_parser.py pdfs/cuts_18-11-2025.pdf СОФИЯ
```

### Automated Scheduling

#### Option 1: Run Continuously

Run the scheduler in continuous mode (checks once per day):

```bash
python scheduler.py --continuous 09:00
```

This will run daily at 9:00 AM. Press Ctrl+C to stop.

#### Option 2: Use Cron (Linux/Mac)

Set up a cron job to run automatically:

```bash
# View cron examples
python scheduler.py --cron-examples

# Edit crontab
crontab -e
```

Add one of these entries:

```cron
# Run every day at 9:00 AM
0 9 * * * cd /path/to/project && ./venv/bin/activate && python scheduler.py --once

# Run every 6 hours
0 */6 * * * cd /path/to/project && ./venv/bin/activate && python scheduler.py --once
```

Replace `/path/to/project` with the actual path to this directory.

## Project Structure

```
electricity-cut-notifier/
├── scraper.py           # Web scraper for ERMZapad website
├── pdf_parser.py        # PDF text extraction and parsing
├── email_notifier.py    # Email notification system
├── main.py              # Main application
├── scheduler.py         # Automated scheduling
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── pdfs/                # Cached PDF files
└── README.md            # This file
```

## Example Output

```
======================================================================
Electricity Cut Notifier
======================================================================
Monitoring cities: СОФИЯ

Fetching planned cuts for next 3 days...
Found 3 documents to check

Processing: Електроразпределителни мрежи Запад ЕАД - планирани прекъсвания за 18.11.2025 г..pdf
----------------------------------------------------------------------
  Total cuts in document: 217
  ALERT: 2 cut(s) affect your monitored cities!
    - ЦЕНТРАЛНА ГР.ЧАСТ СОФИЯ ОБЩ.СЕРДИКА: 08:30 - 16:30
    - ЦЕНТЪР - СОФИЯ ОБЩ.СРЕДЕЦ: 09:00 - 16:15

======================================================================
SUMMARY
======================================================================
PLANNED ELECTRICITY CUTS - ALERT
======================================================================

Date: 18.11.2025
----------------------------------------------------------------------
Location: ЦЕНТРАЛНА ГР.ЧАСТ СОФИЯ ОБЩ.СЕРДИКА
Region: СОФИЯ-ГРАД
Municipality: СЕРДИКА
Time: 08:30 - 16:30

Location: ЦЕНТЪР - СОФИЯ ОБЩ.СРЕДЕЦ
Region: СОФИЯ-ГРАД
Municipality: СРЕДЕЦ
Time: 09:00 - 16:15
```

## Troubleshooting

### PDF Parsing Issues

If no cuts are found in PDFs:
- Check that PyPDF2 extracted text correctly using `inspect_pdf.py`
- The PDF format may have changed - inspect the structure

### Email Not Sending

Common issues:
- **Gmail**: Must use App Password, not regular password
- **Firewall**: Ensure port 587 (or 465) is not blocked
- **2FA**: App passwords required when 2-factor auth is enabled

Test email configuration:
```bash
python email_notifier.py
```

### Scraper Not Finding Documents

- Check if the website structure changed
- Run `debug_scraper.py` to see what HTML is returned
- The site might be temporarily down

## License

This project is for personal/educational use. Please respect the ERMZapad website's terms of service and don't overwhelm their servers with requests.

## Contributing

Feel free to submit issues or pull requests to improve this tool!
# Electricity-cut-notifier
