import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailNotifier:
    """
    Handles sending email notifications about electricity cuts.
    """

    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize the email notifier.

        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            sender_email: Email address to send from
            sender_password: Password or app-specific password for the sender
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_notification(self, recipients, subject, message):
        """
        Sends an email notification.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            message: Email body (plain text)

        Returns:
            bool: True if successful, False otherwise
        """
        if not recipients:
            print("No recipients specified, skipping email notification")
            return False

        if not self.sender_email or not self.sender_password:
            print("Email credentials not configured, skipping email notification")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            # Add plain text body
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)

            # Add HTML body for better formatting
            html_message = self._format_html(message)
            html_part = MIMEText(html_message, 'html', 'utf-8')
            msg.attach(html_part)

            # Connect and send
            print(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")

            # Port 465 uses SSL, port 587 uses TLS
            if self.smtp_port == 465:
                # Use SMTP_SSL for port 465
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    print("Using SSL connection...")
                    print("Logging in...")
                    server.login(self.sender_email, self.sender_password)
                    print(f"Sending email to {len(recipients)} recipient(s)...")
                    server.send_message(msg)
            else:
                # Use SMTP with STARTTLS for port 587 or other ports
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    print("Using TLS connection...")
                    server.starttls()  # Enable encryption
                    print("Logging in...")
                    server.login(self.sender_email, self.sender_password)
                    print(f"Sending email to {len(recipients)} recipient(s)...")
                    server.send_message(msg)

            print("Email sent successfully!")
            return True

        except smtplib.SMTPAuthenticationError:
            print("ERROR: Email authentication failed. Check your email and password.")
            print("For Gmail, you may need to use an App Password instead of your regular password.")
            print("See: https://support.google.com/accounts/answer/185833")
            return False

        except Exception as e:
            print(f"ERROR: Failed to send email: {e}")
            return False

    def _format_html(self, plain_text):
        """
        Converts plain text message to HTML with basic formatting.

        Args:
            plain_text: Plain text message

        Returns:
            str: HTML formatted message
        """
        lines = plain_text.split('\n')
        html_lines = ['<html><body style="font-family: Arial, sans-serif;">']

        for line in lines:
            if '===' in line:
                # Horizontal rule
                html_lines.append('<hr/>')
            elif line.startswith('Date:'):
                # Date header
                html_lines.append(f'<h2 style="color: #d32f2f;">{line}</h2>')
            elif line.startswith('Location:'):
                # Location
                html_lines.append(f'<p style="margin: 5px 0;"><strong>{line}</strong></p>')
            elif line.startswith('  ') or line.startswith('Region:') or line.startswith('Municipality:') or line.startswith('Time:'):
                # Indented details
                html_lines.append(f'<p style="margin: 2px 0 2px 20px; color: #555;">{line}</p>')
            elif line.strip().startswith('PLANNED') or line.strip().startswith('SUMMARY'):
                # Title
                html_lines.append(f'<h1 style="color: #1976d2;">{line}</h1>')
            elif line.strip():
                # Regular text
                html_lines.append(f'<p style="margin: 5px 0;">{line}</p>')
            else:
                # Empty line
                html_lines.append('<br/>')

        html_lines.append('</body></html>')
        return ''.join(html_lines)


def test_email_config(smtp_server, smtp_port, sender_email, sender_password, test_recipient):
    """
    Tests email configuration by sending a test email.

    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP port
        sender_email: Sender email address
        sender_password: Sender password
        test_recipient: Email address to send test to

    Returns:
        bool: True if test successful
    """
    notifier = EmailNotifier(smtp_server, smtp_port, sender_email, sender_password)

    subject = "Test Email - Electricity Cut Notifier"
    message = f"""This is a test email from the Electricity Cut Notifier.

If you received this, your email configuration is working correctly!

Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return notifier.send_notification([test_recipient], subject, message)


def main():
    """
    Interactive email configuration and testing.
    """
    print("=" * 70)
    print("Email Notifier Configuration Test")
    print("=" * 70)
    print()
    print("This will test your email configuration.")
    print()

    # Get configuration from user
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ").strip()
    smtp_port = input("SMTP Port (e.g., 587): ").strip()
    sender_email = input("Your Email Address: ").strip()
    sender_password = input("Your Email Password or App Password: ").strip()
    test_recipient = input("Test Recipient Email: ").strip()

    print()
    print("Testing email configuration...")
    print("-" * 70)

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        print("ERROR: Invalid port number")
        return

    success = test_email_config(
        smtp_server,
        smtp_port,
        sender_email,
        sender_password,
        test_recipient
    )

    if success:
        print()
        print("SUCCESS! Your email configuration is working.")
        print("You can now update these settings in config.json")
    else:
        print()
        print("FAILED. Please check your settings and try again.")


if __name__ == "__main__":
    main()
