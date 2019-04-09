import smtplib

from email.message import EmailMessage


def send_confirmation_mail(email_from, email_to, url, smtp_server):
    msg = EmailMessage()
    msg['Subject'] = "syllabus registration confirmation"
    msg['From'] = email_from
    msg['To'] = email_to

    msg.set_content("You can confirm your registration by clicking on the following link: {}".format(url))

    s = smtplib.SMTP(smtp_server)
    s.send_message(msg)
    s.quit()
