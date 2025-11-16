# Electricity Cut Notifier - GitHub Actions Edition

Automated notification system for planned electricity cuts from ERM Zapad (Bulgarian power company).

## Quick Start

### 1. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/electricity-cut-notifier.git
git push -u origin main
```

### 2. Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Example Value | Description |
|-------------|---------------|-------------|
| `SENDER_EMAIL` | `your-email@gmail.com` | Gmail address for sending |
| `SENDER_PASSWORD` | `xxxx xxxx xxxx xxxx` | Gmail App Password (16 characters) |
| `EMAIL_RECIPIENTS` | `email1@gmail.com,email2@abv.bg` | Recipients (comma-separated) |

**Important for Gmail:** Use App Password (not regular password). Generate at: https://myaccount.google.com/apppasswords

**Error Notifications:** GitHub automatically sends email on workflow failures.

### 3. Configure Cities in config.json

```json
{
  "monitored_cities": ["ГЪРМЕН", "ДЕБРЕН", "САНДАНСКИ"],
  "check_days_ahead": 2,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

**Note:** City names must be in Cyrillic uppercase as they appear in the source PDFs.

### 4. Done!

The system runs automatically every day at 10:00 AM Bulgarian time (8:00 UTC).

## Email Notification Format

```
From: your-email@gmail.com
To: recipient@example.com
Subject: Power Cut Notification - 2 date(s) affected

PLANNED POWER CUTS - NOTIFICATION
======================================================================

Date: 17.11.2025
----------------------------------------------------------------------
Location: ГЪРМЕН
Region: БЛАГОЕВГРАД
Municipality: ГЪРМЕН
Time: 08:30 - 16:30

======================================================================
Source: https://info.ermzapad.bg/webint/vok/avplan.php?PLAN=FYI
```

## Configuration

### config.json

- `monitored_cities`: List of cities to monitor (Cyrillic, uppercase)
- `check_days_ahead`: How many days ahead to check (default: 2)
- `smtp_server`: SMTP server (Gmail: `smtp.gmail.com`)
- `smtp_port`: Port (Gmail: 587)

### GitHub Secrets (3 required)

- `SENDER_EMAIL`: Email address to send from
- `SENDER_PASSWORD`: Password (for Gmail: App Password)
- `EMAIL_RECIPIENTS`: Who receives notifications (comma-separated, no spaces)

## Schedule

Default: Every day at **10:00 AM Bulgarian time** (8:00 UTC)

To change, edit [.github/workflows/check-electricity-cuts.yml](.github/workflows/check-electricity-cuts.yml):

```yaml
schedule:
  - cron: '0 8 * * *'  # 10:00 Bulgarian time
```

Examples:
- `0 7 * * *` = 09:00 Bulgarian time
- `0 9 * * *` = 11:00 Bulgarian time
- `0 6,18 * * *` = 08:00 and 20:00 Bulgarian time

## Manual Run

1. Go to **Actions** tab
2. Select **Check Electricity Cuts**
3. Click **Run workflow**
4. Check your email

## How It Works

```
┌─────────────────────────────────────────────────┐
│   GitHub Actions triggers (daily)               │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│   Downloads PDFs from info.ermzapad.bg          │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│   Extracts power cut information                │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│   Filters by your monitored cities              │
└─────────────┬───────────────────────────────────┘
              │
         ┌────┴────┐
         │         │
      Found    Not found
         │         │
         ▼         ▼
   ┌─────────┐   ┌──────────┐
   │  Send   │   │  Stop    │
   │  email  │   └──────────┘
   └─────────┘
```

## Cost

**Free!** GitHub Actions offers:
- Unlimited minutes for public repositories
- 2000 minutes/month for private repositories
- This workflow uses ~2-3 minutes/day = ~60-90 minutes/month

## Security

- ✅ Passwords stored as GitHub Secrets (encrypted)
- ✅ Never shown in logs
- ✅ Gmail App Password (not your main password)
- ✅ config.json does NOT contain passwords (only cities and settings)

## Gmail Setup

### config.json

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

### GitHub Secrets

- `SENDER_EMAIL`: `your-email@gmail.com`
- `SENDER_PASSWORD`: App Password (16 characters, not regular password!)

**Important**: You must use App Password, not your regular Gmail password.

Create App Password: https://myaccount.google.com/apppasswords

## Troubleshooting

### Workflow not working

1. Check **Actions** tab for logs
2. Verify GitHub Secrets are correctly set
3. Ensure `config.json` is uploaded to repository

### Not receiving emails

1. Check SPAM folder
2. Verify `EMAIL_RECIPIENTS` format (no spaces between emails)
3. Check workflow logs for "Email sent successfully!"

### "Authentication failed" error

- Must use Gmail App Password (16 characters), not regular password
- Check `SENDER_EMAIL` and `SENDER_PASSWORD` in GitHub Secrets
- Ensure App Password is generated correctly: https://myaccount.google.com/apppasswords

## Example Cities

- ГЪРМЕН
- ДЕБРЕН
- САНДАНСКИ
- БЛАГОЕВГРАД
- СОФИЯ
- ПЕРНИК
- КЮСТЕНДИЛ
- ВРАЦА
- МОНТАНА
- ВИДИН

Use exact names as written in PDFs (Cyrillic, uppercase).

## Support

If issues occur:
1. Check Actions logs
2. Check GitHub notifications for errors
3. Verify website is accessible: https://info.ermzapad.bg

## License

For personal/educational use. Please respect ERMZapad website terms of service.
