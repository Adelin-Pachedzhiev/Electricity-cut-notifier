# Troubleshooting Guide

## Email Authentication Failed in GitHub Actions

If you see `ERROR: Email authentication failed` in the GitHub Actions logs:

### Step 1: Verify Secrets Are Set

1. Go to your repository on GitHub
2. Navigate to **Settings → Secrets and variables → Actions**
3. Verify these 3 secrets exist:
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `EMAIL_RECIPIENTS`

### Step 2: Check Secret Values

Click on each secret and verify:

#### SENDER_EMAIL
- ✅ Correct format: `your-email@abv.bg` or `your-email@gmail.com`
- ❌ **NO** spaces before/after
- ❌ **NO** quotes around the email

#### SENDER_PASSWORD
- For **ABV.bg**: Your regular account password
- For **Gmail**: **App Password** (16 characters, NOT your regular password)
- ❌ **NO** spaces before/after
- ❌ **NO** quotes around the password

#### EMAIL_RECIPIENTS
- ✅ Correct format: `email1@example.com,email2@example.com`
- ❌ **NO** spaces after commas
- ❌ **NO** quotes around the list

### Step 3: Check Actions Logs

In the failed workflow run, look for the validation output:

```
✅ Configuration validated successfully
   - Monitoring X city/cities: ...
   - Sender email: your-email@abv.bg
   - Password length: 15 characters  ← Should match your password length
   - Will notify X recipient(s): ...
   - Using SMTP: smtp.abv.bg:465
   - Connection type: SSL
```

**Check:**
- Is the sender email correct?
- Is password length > 0? (If 0, the secret isn't being read)
- Are recipients correct?

### Step 4: Common Issues

#### Issue: Password length shows 0
**Problem:** SENDER_PASSWORD secret is not set or empty
**Solution:**
1. Go to Settings → Secrets → Actions
2. Delete SENDER_PASSWORD if it exists
3. Create new secret with correct password (no spaces!)

#### Issue: Wrong email provider settings
**For ABV.bg:**
```json
{
  "smtp_server": "smtp.abv.bg",
  "smtp_port": 465
}
```

**For Gmail:**
```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

#### Issue: Gmail authentication failed
**Problem:** Using regular password instead of App Password
**Solution:**
1. Go to https://myaccount.google.com/apppasswords
2. Generate new App Password for "Mail"
3. Copy the 16-character password (no spaces)
4. Update SENDER_PASSWORD secret with this password

#### Issue: ABV.bg authentication failed
**Possible causes:**
- Wrong password
- Account locked due to too many failed attempts
- Two-factor authentication enabled (if ABV has it)

**Solution:**
1. Try logging into ABV webmail manually
2. Reset password if needed
3. Update SENDER_PASSWORD secret

### Step 5: Test Locally First

Before pushing to GitHub, test locally:

```bash
export SENDER_EMAIL="your-email@abv.bg"
export SENDER_PASSWORD="your-password"
export EMAIL_RECIPIENTS="test@example.com"

python main.py
```

If it works locally but fails in GitHub Actions, the issue is with your GitHub Secrets configuration.

### Step 6: Check SMTP Server Accessibility

Some SMTP servers may block connections from GitHub's IP ranges.

**For ABV.bg:**
- Usually works fine from GitHub Actions
- Uses port 465 (SSL)

**For Gmail:**
- May require "Less secure app access" (deprecated)
- **Must use App Password**
- Uses port 587 (TLS)

## Configuration Validation Errors

### Error: monitored_cities is empty
```
❌ 'monitored_cities' list is empty - add at least one city
```

**Solution:** Edit `config.json`:
```json
{
  "monitored_cities": ["ГЪРМЕН", "ДЕБРЕН"]
}
```

### Error: Invalid JSON
```
❌ Invalid JSON in 'config.json'
```

**Solution:** Check for:
- Missing commas between items
- Missing quotes around strings
- Trailing commas at the end
- Use a JSON validator: https://jsonlint.com

### Error: config.json not found
```
❌ Configuration file 'config.json' not found!
```

**Solution:**
```bash
cp config.example.json config.json
# Edit config.json with your cities
git add config.json
git commit -m "Add config"
git push
```

## Workflow Not Running

### Check Schedule
The workflow runs daily at 8:00 AM UTC (10:00 AM Bulgarian time).

To test immediately:
1. Go to **Actions** tab
2. Click **Check Electricity Cuts**
3. Click **Run workflow** → **Run workflow**

### Check Workflow File
Verify `.github/workflows/check-electricity-cuts.yml` exists and is valid YAML.

## Email Not Received

### Check Spam Folder
Emails might be in spam, especially the first time.

### Verify Recipients
In the Actions log, look for:
```
Will notify X recipient(s): email1@example.com, email2@example.com
```

Make sure your email is in that list.

### Check Workflow Success
If the workflow shows green checkmark but no email:
- Look for "Email sent successfully!" in logs
- If missing, email sending failed silently

## Debug Mode

To see full configuration details (without password), the validation output shows:
- Cities being monitored
- Sender email
- Password length (to verify it's set)
- Recipients list
- SMTP server and port
- Connection type (SSL/TLS)

Use this to verify everything is configured correctly.

## Still Having Issues?

1. **Check the Actions logs** - Full error details are there
2. **Test locally first** - Easier to debug
3. **Verify all 3 secrets** - Most common issue
4. **Check email provider docs** - Some have special requirements
5. **GitHub will notify you** - You'll get email when workflow fails

## Quick Checklist

Before asking for help, verify:

- [ ] `config.json` exists and has valid JSON
- [ ] `config.json` has at least one city in `monitored_cities`
- [ ] `config.json` has correct SMTP server and port
- [ ] GitHub Secret `SENDER_EMAIL` is set (no quotes, no spaces)
- [ ] GitHub Secret `SENDER_PASSWORD` is set (no quotes, no spaces)
- [ ] GitHub Secret `EMAIL_RECIPIENTS` is set (comma-separated, no spaces)
- [ ] For Gmail: Using App Password, not regular password
- [ ] Can login to email account manually (not locked)
- [ ] Tested locally with same credentials (works?)
- [ ] Checked Actions logs for validation output
- [ ] Checked password length in logs (not 0)
