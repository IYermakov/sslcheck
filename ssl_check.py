import ssl
import socket
import datetime
import argparse
from datetime import date, timedelta
from dateutil.parser import parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_SSL_Expiry_Date(host, port=443):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=host,
    )
#if you want to use it as lambda
    conn.settimeout(3.0)
    conn.connect((host, port))
    ssl_info = conn.getpeercert()

    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    certdate = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    return certdate

def main(sitesfile):

    sender_email = "script@gmail.com"
    receiver_email = "notregisterednick@gmail.com"
#    password = input("Type your password and press enter:")

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    with open(sitesfile, "r") as sites_file:
      array=[]
      for line in sites_file:
        array.append(line.split("\n", 1)[0])

    judgementday = datetime.datetime.now() + timedelta(days=7)
    html = """\
    <html>
       <head>
          <style type="text/css">
             .tg  {{border-collapse:collapse;border-spacing:0;}}
             .tg td{{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}}
             .tg th{{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;}}
             .tg .tg-norm{{text-align:left;vertical-align:top;color:black;}}
             .tg .tg-alarm{{text-align:left;vertical-align:top;color:red;}}
          </style>
       </head>
       <body>
          <table class="tg">
    """

    for sites in array:
      certdate = get_SSL_Expiry_Date(sites, 443)
      ooo=str(certdate-judgementday).split(',', 1)[0]
#      html=html+"{} will be expired in {}<br>".format(sites,ooo)
      aaa=int(str(certdate-judgementday).split(' ', 1)[0])
      if aaa>7:
        tgstyle="tg-norm"
      else:
        tgstyle="tg-alarm"
      print(tgstyle)
      html=html+"<tr><th class={}>{}</th></tr> <tr><td class={}>{}</td></tr>".format(tgstyle,sites,tgstyle,ooo)

    html=html+"</table></body></html>"
    print(html)

    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#    with smtplib.SMTP('localhost') as server:
#        server.login(sender_email, password)
#        server.sendmail(sender_email, receiver_email, message.as_string())
#        server.quit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Sites list')
    parser.add_argument('sitesfile', type=str, help='File contains list of domains to check')
#    parser.add_argument('sender', type=str, help='Email sender')
#    parser.add_argument('receiver', type=str, help='Email receiver')
    args = parser.parse_args()
    main(args.sitesfile)
