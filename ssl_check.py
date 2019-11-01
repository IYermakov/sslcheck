import ssl
import socket
import datetime
import argparse
from datetime import date, timedelta
from dateutil.parser import parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import operator

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
             <tr><th class=th>Certificate</th><th class=th>Issuer</th><th class=th>Days till expire</th></tr>
    """
    d={}
    for sites in array:
      certinfo = get_SSL_Expiry_Date(sites, 443)
      try:
        daystoexpire=int(str(certinfo[0]-datetime.datetime.now()).split(' ', 1)[0])
      except:
        daystoexpire=999
      d[sites]=[daystoexpire,certinfo[1]]

    for items in sorted(d.items(), key=operator.itemgetter(1)):
      if items[1][0]>7:
        tgstyle="tg-norm"
      else:
        tgstyle="tg-alarm"
      html=html+"<tr><td class={}>{}</td> <td class=tg-norm>{}</td> <td class={}>{} days</td></tr>".format(tgstyle,items[0],items[1][1],tgstyle,items[1][0])

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
