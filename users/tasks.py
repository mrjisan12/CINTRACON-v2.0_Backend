from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


def _otp_html(otp, title, color, subtitle):
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:30px;border:1px solid #e5e7eb;border-radius:12px">
      <h2 style="color:#3b82f6;margin:0 0 8px">CINTRACON</h2>
      <p style="color:#6b7280;margin:0 0 24px;font-size:14px">Student Social Platform</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin-bottom:24px">
      <p style="font-size:16px;color:#111827">{subtitle}</p>
      <div style="background:#f3f4f6;border-radius:8px;padding:20px;text-align:center;margin:20px 0">
        <span style="font-size:36px;font-weight:bold;letter-spacing:12px;color:{color}">{otp}</span>
      </div>
      <p style="color:#6b7280;font-size:13px">Valid for <strong>10 minutes</strong>. Do not share this code with anyone.</p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
      <p style="color:#9ca3af;font-size:12px;text-align:center">CINTRACON &copy; 2025. If you didn't request this, please ignore.</p>
    </div>
    """


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, email, otp):
    try:
        send_mail(
            subject='CINTRACON — Email Verification',
            message=f'Your email verification code is: {otp}. Valid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=_otp_html(
                otp, 'Email Verification', '#1d4ed8',
                'Enter this code to verify your email address:'
            ),
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, email, otp):
    try:
        send_mail(
            subject='CINTRACON — Password Reset',
            message=f'Your password reset code is: {otp}. Valid for 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=_otp_html(
                otp, 'Password Reset', '#ef4444',
                'You requested a password reset. Use this code:'
            ),
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_announcement_notification_email(self, recipient_emails, title, content):
    try:
        from django.core.mail import send_mass_mail
        messages = [
            (
                f'CINTRACON Announcement: {title}',
                content,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            for email in recipient_emails
        ]
        send_mass_mail(messages, fail_silently=True)
    except Exception as exc:
        raise self.retry(exc=exc)
