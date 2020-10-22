import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def sendMail(my_email, recipient_email, title, msg, pngfiles):
    """
    완성된 기사와 차트를 이메일로 보내는 함수

    params:
        my_email : 내 email 주소
        recipient_email : 받을 상대방의 email 주소
        title : 기사 제목
        msg : 기사 제목 및 내용
        feed_num: 공시의 고유번호
    """

    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp.login(my_email, 'cyuidhhqqepdqhmo') #나의 앱비밀번호
    # 이메일 TEXT
    msg = MIMEMultipart(msg)
    #msg = MIMEText(msg) # 기사내용, 제목 등등

    #이메일 IMAGE

    filename = ['Chart', 'Bar']
    for i in range(0,2):
      fp = open(pngfiles[i], 'rb')
      img = MIMEImage(fp.read())
      fp.close()
      # 첨부한 파일의 파일이름을 입력합니다. (이 구문이 없으면 noname으로 발송됩니다.)
      img.add_header('Content-Disposition', filename[i], filename=pngfiles[i])
      msg.attach(img)

    # 이메일 제목
    msg['Subject'] = title

    #Sending Email
    smtp.sendmail(my_email, recipient_email, msg.as_string())
    smtp.quit()
