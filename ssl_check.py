#from datetime import datetime
#from OpenSSL import crypto as c

import ssl
#import OpenSSL
import socket
import datetime
from datetime import date, timedelta
from dateutil.parser import parse

def get_SSL_Expiry_Date(host, port=443):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=host,
    )
    conn.settimeout(3.0)
    conn.connect((host, port))
    ssl_info = conn.getpeercert()

    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    certdate = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    judgementday = datetime.datetime.now() + timedelta(days=7)

    print "send letter" if certdate<judgementday else "no"

get_SSL_Expiry_Date("adstartmedia.affise.com", 443)