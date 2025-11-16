# GitHub Actions Notifications Setup

GitHub Actions will automatically notify you when workflows fail. No need for custom admin email!

## 🔔 How to Enable Notifications

### Option 1: Email Notifications (Recommended)

1. Go to your GitHub profile: https://github.com/settings/notifications
2. Under **Actions**, ensure these are enabled:
   - ✅ **Send notifications for failed workflows only**
   - ✅ **Email**

3. You'll receive emails like this when the workflow fails:

```
From: notifications@github.com
Subject: [YOUR_USERNAME/electricity-cut-notifier] Run failed: Check Electricity Cuts

The workflow "Check Electricity Cuts" in YOUR_USERNAME/electricity-cut-notifier failed.

View the workflow run:
https://github.com/YOUR_USERNAME/electricity-cut-notifier/actions/runs/123456789
```

### Option 2: GitHub Mobile App

1. Install GitHub Mobile app (iOS/Android)
2. Enable push notifications
3. Get instant alerts on your phone when workflows fail

### Option 3: Watch the Repository

1. Go to your repository page
2. Click **Watch** (top right)
3. Select **Custom** → Check **Actions**
4. You'll get notifications for all workflow runs

## 📧 What You'll Receive

When the workflow fails, GitHub will email you:

- ✅ Workflow name: "Check Electricity Cuts"
- ✅ Run status: Failed
- ✅ Link to view full logs
- ✅ Commit that triggered the run
- ✅ Timestamp

## 🔍 Viewing Error Details

When you receive a failure notification:

1. Click the link in the email (or go to **Actions** tab)
2. Click on the failed workflow run
3. Expand the **Run electricity cut checker** step
4. See full error details, including:
   - Python traceback
   - Error message
   - All print statements

## 📋 Common Errors and Solutions

### Authentication Failed
```
ГРЕШКА / ERROR
======================================================================
Възникна грешка: Authentication failed
```

**Solution:** Check your GitHub Secrets:
- `SENDER_EMAIL` - correct email address?
- `SENDER_PASSWORD` - correct password?

### Connection Timeout
```
ГРЕШКА / ERROR
======================================================================
Възникна грешка: Connection timeout
```

**Solution:** The website might be temporarily down. Check https://info.ermzapad.bg manually.

### Invalid Recipients
```
ГРЕШКА / ERROR
======================================================================
Възникна грешка: Invalid email address
```

**Solution:** Check `EMAIL_RECIPIENTS` secret format:
- Correct: `email1@example.com,email2@example.com`
- Wrong: `email1@example.com, email2@example.com` (space after comma)

## 🛠️ GitHub Notification Settings

### Customize What You Get Notified About

Go to: https://github.com/settings/notifications

**Recommended settings:**
- ✅ Actions: **Failed workflows only** (don't spam on success)
- ✅ Email: Your email address
- ✅ Web + Mobile: Enable both

**Optional settings:**
- Include your own updates (if you want notifications even when you manually trigger)
- Watching: Only repos you care about

## 🔕 Disable Notifications (Not Recommended)

If you want to disable GitHub notifications:

1. Go to: https://github.com/settings/notifications
2. Under **Actions**, uncheck **Email**

**Note:** You'll lose visibility into workflow failures!

## ⚡ Quick Test

Want to see what a failure notification looks like?

1. **Temporarily** set wrong password in GitHub Secrets
2. Go to **Actions** tab → **Run workflow**
3. Wait ~1 minute for it to fail
4. Check your email for GitHub notification
5. **Fix** the password back to correct value

## 📱 GitHub Mobile App Notifications

Download GitHub Mobile for instant notifications:

- **iOS:** https://apps.apple.com/app/github/id1477376905
- **Android:** https://play.google.com/store/apps/details?id=com.github.android

Enable push notifications in the app settings.

## 🎯 Summary

✅ **No custom admin email needed** - GitHub handles everything
✅ **Automatic notifications** - Emails sent on workflow failures
✅ **Full error details** - Click link to see logs
✅ **Mobile alerts** - Install GitHub Mobile app
✅ **Customizable** - Control what you get notified about

## 🔗 Useful Links

- GitHub Notifications Settings: https://github.com/settings/notifications
- GitHub Mobile: https://mobile.github.com
- Your repository Actions: https://github.com/YOUR_USERNAME/electricity-cut-notifier/actions
