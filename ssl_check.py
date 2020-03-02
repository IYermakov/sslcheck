import ssl
import socket
import datetime
import argparse
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import operator
import requests
import json
import os
from string import Template

def post_blocks_to_slack(text, blocks = None):
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': os.environ['SLACK_TOKEN'].encode('utf-8'),
        'channel': "#alerts",
        'username': "script",
        'blocks': blocks if blocks else None
    }).json()

def get_expiry_date(host, port=443):
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
      return 'connection error', 'connection error'


def main(sitesfile):

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = 'script@localhost'
    receivers = ['user1@gmail.com', 'user2@ua.fm']

    with open(sitesfile, "r") as sites_file:
      array=[]
      for line in sites_file:
        array.append(line.split("\n", 1)[0])

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
    blocks = """[
      {
          "type": "section",
          "fields": [
              {
                  "type": "mrkdwn",
                  "text": "*Certificate* and *Issuer*"
              },
              {
                  "type": "mrkdwn",
                  "text": "*Days till expire*"
              }
          ]
      },
    """
    t = Template('{"type": "section","fields": [{"type": "mrkdwn","text": "${one}   ${two}"},{"type": "mrkdwn","text": "${three}"}]},\n')
    d={}
    for sites in array:
      certinfo = get_expiry_date(sites, 443)
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
      blocks = blocks + t.safe_substitute(one=items[0],two=items[1][1],three=items[1][0])
    html=html+"""
        </table>
      </body>
    </html>
    """
    blocks=blocks[:-2]+"]"
#    print(html)
#    print(blocks)
    post_blocks_to_slack("Script info",blocks)

    message.attach(MIMEText(html, "html"))
    with smtplib.SMTP('localhost') as server:
       for receiver in receivers:
         try:
           server.sendmail(message["From"], receiver, message.as_string())
         except:
           print("error sending message to {}".format(receiver))
       server.quit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Sites list')
    parser.add_argument('sitesfile', type=str, help='File contains list of domains to check')
    args = parser.parse_args()
    main(args.sitesfile)
