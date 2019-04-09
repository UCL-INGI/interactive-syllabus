import smtplib

from email.message import EmailMessage


def _send_confirmation_email(email_from, email_to, url, serv):
    msg = EmailMessage()
    msg['Subject'] = "syllabus registration confirmation"
    msg['From'] = email_from
    msg['To'] = email_to

    msg.set_content("You can confirm your registration by clicking on the following link: {}".format(url))
    serv.send_message(msg)


def send_confirmation_mail(email_from, email_to, url, smtp_server):
    s = smtplib.SMTP(smtp_server)
    _send_confirmation_email(email_from, email_to, url, s)
    s.quit()


def send_authenticated_confirmation_mail(email_from, email_to, url, smtp_server, username, password):
    s = smtplib.SMTP_SSL(smtp_server)
    s.login(username, password)
    _send_confirmation_email(email_from, email_to, url, s)
    s.quit()


