import smtplib

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address


class EmailBackend(EmailBackend):

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False

        to_emails = getattr(settings, 'HIJACK_EMAILS', [])
        cc_emails = getattr(settings, 'HIJACK_CC_EMAILS', [])
        bcc_emails = getattr(settings, 'HIJACK_BCC_EMAILS', [])

        if not to_emails:
            return False
        email_message.to = to_emails

        if email_message.cc:
            email_message.cc = cc_emails

        if email_message.bcc:
            email_message.bcc = bcc_emails

        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes())
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
