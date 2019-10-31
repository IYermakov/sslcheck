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
    ssl.match_hostname = lambda cert, hostname: True
    context = ssl.create_default_context()
    try:
      ssock=socket.socket(socket.AF_INET)
      conn = context.wrap_socket(ssock,server_hostname=host)
      conn.connect((host, port))
      ssl_info = conn.getpeercert()
      ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
      certdate = datetime.datetime.strptime(str(ssl_info['notAfter']), ssl_date_fmt)
      issuer = dict(x[0] for x in ssl_info['issuer'])
      certissuer = issuer['commonName']
      return certdate, certissuer
    except:
      return 'connectionerror','connectionerror'

def main(sitesfile, sender_email, receiver_email):

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
             .tg .tg-norm{color:black; font-size: 17px;}
             .tg .tg-alarm{color:black; font-size: 17px; background: red; font-weight: bold;}
             .tg {width: 100%; margin: 0 auto; max-width: 900px; border-radius: 5px; border: 1px solid black;}
             tr {text-align: center; height: 40px}
             .top {background: black; font-size: 20px; font-width: bold; color: white}
             tbody {background: #dcdbdb;}
          </style>
       </head>
       <body>
          <table class="tg">
             <tr class="top"><th class=th>Certificate</th><th class=th>Issuer</th><th class=th>Days till expire</th></tr>
    """

    for sites in array:
      certinfo = get_SSL_Expiry_Date(sites, 443)
      try:
        daystoexpire=str(certinfo[0]-judgementday).split(',', 1)[0]
        aaa=int(str(certinfo[0]-judgementday).split(' ', 1)[0])
        if aaa>7:
          tgstyle="tg-norm"
        else:
          tgstyle="tg-alarm"
      except:
        tgstyle="tg-alarm"
        daystoexpire='NULL'
      html=html+"<tr><td class={}>{}</td> <td class=tg-norm>{}</td> <td class={}>{}</td></tr>".format(tgstyle,sites,certinfo[1],tgstyle,daystoexpire)

    html=html+"</table></body></html>"
    print(html)
    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP('localhost') as server:
       server.sendmail(sender_email, receiver_email, message.as_string())
       server.quit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Sites list')
    parser.add_argument('sitesfile', type=str, help='File contains list of domains to check')
    parser.add_argument('sender', type=str, help='Email sender')
    parser.add_argument('receiver', type=str, help='Email receiver')
    args = parser.parse_args()
    main(args.sitesfile, args.sender, args.receiver)
