import smtplib
from email.mime.text import MIMEText

 
def sendMail(my_email, recipient_email, msg):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(my_email, 'cyuidhhqqepdqhmo') 
    msg = MIMEText(msg)
    msg['Subject'] = '김수완 Test Mail 입니다'
    smtp.sendmail(my_email, recipient_email, msg.as_string())
    smtp.quit()

sendMail('tndhks3837@gmail.com', 'swan3837@naver.com', '실습 테스트 메일입니다') 

