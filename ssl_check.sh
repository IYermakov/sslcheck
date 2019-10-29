#!/bin/bash

export PATH=/bin:/sbin:/usr:/usr/bin:/usr/sbin:/usr/local:/usr/local/bin:/usr/local/sbin

host=$(echo $1 | cut -d, -f1)
port=$2
sni=$(echo $1 | cut -d, -f1)
PROFILE=$3
proto=$4
ZONE_ID=$(echo $1 | cut -d, -f2)
IS_CUSTOM=""
COMMENT="$(echo $1 | cut -d, -f3)"

### SSL section

if [ -z "$sni" ]
then
    servername=$host
else
    servername=$sni
fi

if [ -n "$proto" ]
then
    starttls="-starttls $proto"
fi

end_date=`openssl s_client -servername $servername -host $host -port $port -showcerts $starttls -prexit </dev/null 2>/dev/null |
          sed -n '/BEGIN CERTIFICATE/,/END CERT/p' |
          openssl x509 -text 2>/dev/null |
          sed -n 's/ *Not After : *//p'`

if [ -n "$end_date" ]
then
    end_date_seconds=`date '+%s' --date "$end_date"`
    now_seconds=`date '+%s'`
    days=$(echo "($end_date_seconds-$now_seconds)/24/3600" | bc)
else
    days="N/A"
fi

issue_dn=`openssl s_client -servername $servername -host $host -port $port -showcerts $starttls -prexit </dev/null 2>/dev/null |
          sed -n '/BEGIN CERTIFICATE/,/END CERT/p' |
          openssl x509 -text 2>/dev/null |
          sed -n 's/ *Issuer: *//p'`

if [ -n "$issue_dn" ]
then
    issuer=`echo $issue_dn | sed -n 's/.*CN=*//p'`
else
    issuer="N/A"
fi

end_date=`openssl s_client -servername $servername -host $host -port $port -showcerts $starttls -prexit </dev/null 2>/dev/null |
          sed -n '/BEGIN CERTIFICATE/,/END CERT/p' |
          openssl x509 -text 2>/dev/null | grep 'Not After' | awk '{print $4,$5,$7}'`

if [ -z "$end_date" ]
then
    end_date="N/A"
fi

start_date=`openssl s_client -servername $servername -host $host -port $port -showcerts $starttls -prexit </dev/null 2>/dev/null |
            sed -n '/BEGIN CERTIFICATE/,/END CERT/p' |
            openssl x509 -text 2>/dev/null | grep 'Not Before' | awk '{print $3,$4,$6}'`

if [ -z "$start_date" ]
then
    start_date="N/A"
fi

if [ -n "$ZONE_ID" ]
then
    ip=$(aws --profile=$PROFILE route53 list-resource-record-sets --hosted-zone-id $ZONE_ID --query "ResourceRecordSets[?Type == 'A']" | 
         jq '.[0].ResourceRecords[0].Value' | head -1 | sed 's/"//g')
    if [ "$ip" == "null" ]
    then
         ip=$(aws --profile=$PROFILE route53 list-resource-record-sets --hosted-zone-id $ZONE_ID --query "ResourceRecordSets[?Type == 'A']" | 
         jq '.[0].AliasTarget.DNSName' | head -1 | sed 's/"//g')
    fi

    if [ "$ip" == "null" ] || [ -z "$ip" ]
    then
        ip="N/A"
    fi
else
    ip=$(host $host | head -1 | grep 'has address' | awk '{print $4}')
    if [ -z "$ip" ]
    then
        ip="N/A"
    fi
    IS_CUSTOM="Custom"
fi

cn=`openssl s_client -servername $servername -host $host -port $port -showcerts $starttls -prexit </dev/null 2>/dev/null | openssl x509 -text 2>/dev/null | grep 'CN='`

if [ -z "$cn" ]
then
    sni="N/A"
else
    sni=$(python3 -c 'import sys; txt = sys.argv[1].strip() ; print(txt[txt.rfind("=")+1:].lower())' "$cn")
fi

### WHOIS section

if [ -n "$ZONE_ID" ]
then
    STARTS=$(whois $servername | grep -E -i '([Cc]reation [Dd]ate:|[Cc]reated:|[Rr]egistered on:)' | cut -d: -f2 | cut -dT -f1 | awk '{print $1}' | sed s/'\s'//g | head -1)
    if [ -z "$STARTS" ]; then
      STARTS="N/A"
    fi

    EXPIRES=$(whois $servername | grep -E -i '([Ee]xpiry [Dd]ate:|paid-till:|[Ee]xpire Date:)' | cut -d: -f2,3,4 | awk '{print $1}' | sed s/'\s'//g | head -1)
    if [ -z "$EXPIRES" ]; then
      EXPIRES="N/A"
    fi

    DAYS=""
    if [ "$EXPIRES" != "N/A" ]
    then
      END_DATE_SECONDS=`date '+%s' --date "$EXPIRES"`
      NOW_SECONDS=`date '+%s'`
      DAYS=$(echo "($END_DATE_SECONDS-$NOW_SECONDS)/24/3600" | bc)
    else
      DAYS="N/A"
    fi
else
    STARTS="N/A"
    EXPIRES="N/A"
    DAYS="N/A"
fi

EXPIRES=$(echo $EXPIRES | cut -dT -f1)

# print output to stdout
echo "$host,$ip,$days,$issuer,$sni,$start_date,$end_date,$DAYS,$STARTS,$EXPIRES,$IS_CUSTOM,$COMMENT"

