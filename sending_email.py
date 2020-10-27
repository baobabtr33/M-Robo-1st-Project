import os, copy
import smtplib               # SMTP 라이브러리
from string import Template # 문자열 템플릿 모듈을 위함.
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
import logging.config

class EmailHTMLImageContent:
    """
    이메일에 담길 이미지가 포함된 컨텐츠 생성
    """

    def __init__(self, str_subject, str_image_file_name1, str_cid_name1, str_image_file_name2, str_cid_name2, template, template_params):
        """
        params :
            str_subject : 이메일 제목
            str_image_file_name1 : 이미지 파일1 (경로포함)
            str_cid_name1 : 이미지가 들어갈 이름1
            str_image_file_name2 : 이미지 파일2 (경로포함)
            str_cid_name2 : 이미지가 들어갈 이름2
            template : string.Template() 형태로 html 형성
            template_params : dict 형식으로 변수를 받음
        return :
            이메일에 담길 이미지와 텍스트 임베딩
        """

        assert isinstance(template,Template)
        assert isinstance(template_params, dict)
        self.msg = MIMEMultipart()

        # 이메일 제목
        self.msg['Subject'] = str_subject

        # 이메일 본문(text)
        str_msg = template.safe_substitute(**template_params)  # ${변수} 치환하며 문자열 만든다
        mime_msg = MIMEText(str_msg, 'html')  # MIME HTML 문자열을 만든다
        self.msg.attach(mime_msg)

        # 이메일 본문에 주가차트 임베딩
        assert template.template.find("cid:" + str_cid_name1) >= 0, 'template must have cid for embedded image.'
        assert os.path.isfile(str_image_file_name1), 'image file does not exist.'
        with open(str_image_file_name1, 'rb') as img_file:
            mime_img = MIMEImage(img_file.read())
            mime_img.add_header('Content-ID', '<' + str_cid_name1 + '>')
        self.msg.attach(mime_img)

        # 이메일 본문에 바차트 임베딩
        assert template.template.find("cid:" + str_cid_name2) >= 0, 'template must have cid for embedded image.'
        assert os.path.isfile(str_image_file_name2), 'image file does not exist.'
        with open(str_image_file_name2, 'rb') as img_file:
            mime_img = MIMEImage(img_file.read())
            mime_img.add_header('Content-ID', '<' + str_cid_name2 + '>')
        self.msg.attach(mime_img)


    def get_message(self, str_from_email_addr, str_to_eamil_addrs):
        """
        발신자, 수신자리스트를 이용하여 보낼메시지를 만든다
        params:
            str_from_email_addr : 발신자
            str_to_eamil_addrs : 수신자 리스트
        return:
            mm : 발신자, 수신자 리스트
        """

        mm = copy.deepcopy(self.msg)
        mm['From'] = str_from_email_addr  # 발신자
        mm['To'] = ",".join(str_to_eamil_addrs)  # 수신자리스트
        return mm

class EmailSender:
    """이메일 발송자"""

    def __init__(self):
        """
        자신의 gamil 계정과 앱 비밀번호 넣기
        """

        self.ss = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.ss.login('tndhks3837@gmail.com', 'cyuidhhqqepdqhmo')  # 나의 앱비밀번호

    def send_message(self, EmailHTMLImageContent, str_from_email_addr, str_to_email_addrs):
        """
        이메일 발송
        params:
            EmailHTMLImageContent : 이미지, 텍스트가 임베딩 되어 있는 콘텐츠
            str_from_email_addr : 발신자자
           str_to_email_addrs : 수신자 리스트
        """

        cc = EmailHTMLImageContent.get_message(str_from_email_addr, str_to_email_addrs)
        self.ss.send_message(cc, from_addr=str_from_email_addr, to_addrs=str_to_email_addrs)
        del cc


def Sending_Final_Email(link, title, first_sen, second_sen, third_sen, final_sen, chart_file, str_from_email_addr, str_to_email_addrs):
    """
    기사, 제목, 이미지를 받아와 이메일 보내는 함수
    params :
        link : 공시 url
        title: 기사 제목(이메일 제목)
        first_sen: 첫 번째 문장
        second_sen: 두 번째 문장
        third_sen: 세 번째 문장
        final_sen: 마지막 문장
        chart_file: 차트 경로가 포함된 이미지 파일
        str_from_email_addr: 수신자
        str_to_email_addrs: 발신자 리스트
    return:
        이메일 보냄
    """

    template = Template("""<html>
                                <head></head>
                                <body>
                                    <img src="cid:chart"><br>
                                    ${first_sen} <br>
                                    ${second_sen} <br>
                                    ${third_sen} <br>
                                    ${final_sen} <br>
                                    <a href= S{link}>
                                    공시전문으로 이동
                                    </a> <br>
                                    <img src="cid:bar"><br>
                                    </a><br>
                                </body>
                            </html>""")


    emailHTMLImageContent = EmailHTMLImageContent(str_subject=title, str_image_file_name1=chart_file[0],
                                                str_cid_name1='chart', str_image_file_name2=chart_file[1],
                                                str_cid_name2='bar', template=template,
                                                template_params= {'first_sen': first_sen, 'second_sen': second_sen,
                                                'third_sen': third_sen, 'final_sen': final_sen,
                                                'link': link} )

    emailsender= EmailSender()
    emailsender.send_message(EmailHTMLImageContent=emailHTMLImageContent, str_from_email_addr=str_from_email_addr,
                             str_to_email_addrs=str_to_email_addrs)



