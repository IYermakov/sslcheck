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

    sender_email = "notregisterednick@gmail.com"
    receiver_email = "notregisterednick@gmail.com"
#    password = input("Type your password and press enter:")

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    with open(sitesfile, "r") as sites_file:
        array = []
	for line in sites_file:
    	    array.append(line.split("\n", 1)[0])

    judgementday = datetime.datetime.now() + timedelta(days=7)
    html = """\
    <html>
        <body>
            <p>Hi,<br>
    """
#colorize text
    for sites in array:
	certdate = get_SSL_Expiry_Date(sites, 443)
	ooo=str(certdate-judgementday).split(',', 1)[0]
        html=html+"{} will be expired in {}<br>".format(sites,ooo)
    html=html+"</p></body></html>"
    print html

    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    with smtplib.SMTP('localhost') as server:
#	server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Sites list')
    parser.add_argument('sitesfile', type=str, help='File contains list of domains to check')
#    parser.add_argument('sender', type=str, help='Email sender')
#    parser.add_argument('receiver', type=str, help='Email receiver')
    args = parser.parse_args()
    main(args.sitesfile)