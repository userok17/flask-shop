from flask import render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from . import app


def send_mail(to_email, subject, template, **kwargs):
    smtp_obj = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
    smtp_obj.ehlo()
    smtp_obj.starttls()
    
    smtp_obj.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    
    msg = MIMEMultipart('alternative')
    
    msg['Subject'] = app.config['FLASKY_MAIL_SUBJECT_PREFIX']  + ' '+ subject
    msg['From'] = formataddr((str(Header(app.config['FLASKY_FROM_NAME'], 'utf-8')), app.config['FLASKY_FROM']))
    msg['To'] = to_email
    msg['Charset'] = 'utf-8'
    
    text = render_template(template+'.txt', **kwargs)
    html = render_template(template+'.html', **kwargs)
    
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    smtp_obj.sendmail(app.config['MAIL_USERNAME'], to_email, msg.as_string())
    smtp_obj.quit()