import smtplib

from email.message import EmailMessage


def _send_confirmation_email(email_from, email_to, url, serv):
    msg = EmailMessage()
    msg['Subject'] = "syllabus registration confirmation"
    msg['From'] = email_from
    msg['To'] = email_to

    msg.set_content("You can confirm your registration by clicking on the following link: {}".format(url))
    serv.send_message(msg)


def send_confirmation_mail(email_from, email_to, url, smtp_server, smtp_port=None, use_ssl=True):
    smtp_type = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    s = smtp_type(smtp_server, port=smtp_port if smtp_port is not None else 0)  # 0 == default port (465 for ssl, 25 for unencrypted)
    _send_confirmation_email(email_from, email_to, url, s)
    s.quit()


def send_authenticated_confirmation_mail(email_from, email_to, url, smtp_server, username, password, smtp_port=None):
    s = smtplib.SMTP_SSL(smtp_server, port=smtp_port if smtp_port is not None else 0)  # 0 == default port (465)
    s.login(username, password)
    _send_confirmation_email(email_from, email_to, url, s)
    s.quit()


