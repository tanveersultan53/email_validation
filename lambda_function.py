import json
import dns.resolver

import re, sys, smtplib

from constant import find_role

#Check if pythondns libraries exist and import them
try:
    import dns.resolver
except Exception as exc:
    print('EmailValidator requires "pythondns" libraries')
    print(exc)
    quit()

#Address used for SMTP MAIL FROM command
fromAddress = 'test@google.com'
validList = []

#Check the syntax
def checkSyntax(emailAddress):
    try:
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        addressToVerify = str(emailAddress)
        match = re.match(regex, addressToVerify)
        if match == None:
            return False
        else:
            return True
    except Exception as exc:
        print(emailAddress + ' is not a valid email address')
        print(exc)
        return -1

#Get domain for DNS lookup
def getHost(emailAddress):
    try:
        return emailAddress.split('@')[1]
    except Exception as exc:
        print(emailAddress + ' is not a valid email address')
        print(exc)
        return -1

#DNS MX records lookup
def resolveMX(emailHost,email):
    global hostItems
    hostDict={}
    try:
        records = dns.resolver.query(email, 'MX')
        ecords = dns.resolver.resolve(email, 'A')
    except Exception as exc:
        print('Could not extract records from host.')
        print(exc)
        validList.append({
            "email":email,
            "email_host":emailHost,
            "status_code":"unknown",
            "reason":"Could not extract records from host",
            "account":{
                "role":"",
                "disabled":"unknown",
                "fullMailbox":"unknown"
            },
            "dns":{
                "type":"",
                "record":""
            },
            "provider":"other"
         })
        return -1
    for r in records:
        hostDict[r.exchange] = r.preference
    for r in ecords:
        print()
        print(r.to_text(),"!!!!")
    hostItems = list(hostDict.items())
    hostItems.sort()

#Email user lookup
def checkEmail(emailAddress,host_name):
    result = True
    code = 400
    smtp = smtplib.SMTP()
    smtp.set_debuglevel(0)
    for x in hostItems:
        try:
            host = x[0][:-1]
            host = b'.'.join(host).decode("utf-8")
            connectLog = smtp.connect(host)
            print(connectLog)
            heloLog = smtp.helo(smtp.local_hostname)
            print(heloLog)
        except Exception as exc:
            print(exc)
            continue
        else:
            result = False
            break
    if result:
        print('Could not resolve any hosts for: ' + emailAddress)
        return -1
    try:
        smtp.mail(fromAddress)
        code, message = smtp.rcpt(emailAddress)
        smtp.quit()
        # print(code)
    except Exception as exc:
        # print('Email is not valid.')
        print(exc)
    else:
        provider = "google" if "google" in connectLog else "other"
        if code == 250:
            # print('Email: ' + emailAddress + ' is valid!')
            # validList.append({emailAddress:"varify"})
            validList.append(validList.append({
            "email":emailAddress,
            "email_host":host_name,
            "status_code":"deliverable",
            "reason":f"{message}",
            "account":{
                "role":Role
                "disabled":"unknown",
                "fullMailbox":"unknown"
            },
            "dns":{
                "type":"",
                "record":""
            },
            "provider":provider
            }))
        else:
            # validList.append({emailAddress:"not varify"})
            validList.append(validList.append({
            "email":emailAddress,
            "email_host":host_name,
            "status_code":"undeliverable",
            "reason":f"{message}",
            "account":{
                "role":"",
                "disabled":"unknown",
                "fullMailbox":"unknown"
            },
            "dns":{
                "type":"",
                "record":""
            },
            "provider":provider
         }))




list_of_emails = ["tanveer6959612@gmail.com","tas@gmail.com","hello@lyne.ai"]

def lambda_handler(list_of_emails=None, context=None):
    for item in list_of_emails:
        if not checkSyntax(item) == -1:
            host = getHost(item)
            if not host == -1:
                if not resolveMX(host,email=item) == -1:
                    checkEmail(item,host)
        # else:
        #     validList.append({
        #         str(item):{
        #             "syntax_flag":False,
        #             "status":None,
        #             "server_logs":None
        #         }
        #     })
    return {
        'statusCode': 200,
        'body': validList
    }



print(lambda_handler(list_of_emails=list_of_emails))

# def get_records(domain):
#     """
#     Get all the records associated to domain parameter.
#     :param domain: 
#     :return: 
#     """
#     ids = [
#         'NONE',
#         'A',
#         'NS',
#         'MD',
#         'MF',
#         'CNAME',
#         'SOA',
#         'MB',
#         'MG',
#         'MR',
#         'NULL',
#         'WKS',
#         'PTR',
#         'HINFO',
#         'MINFO',
#         'MX',
#         'TXT',
#         'RP',
#         'AFSDB',
#         'X25',
#         'ISDN',
#         'RT',
#         'NSAP',
#         'NSAP-PTR',
#         'SIG',
#         'KEY',
#         'PX',
#         'GPOS',
#         'AAAA',
#         'LOC',
#         'NXT',
#         'SRV',
#         'NAPTR',
#         'KX',
#         'CERT',
#         'A6',
#         'DNAME',
#         'OPT',
#         'APL',
#         'DS',
#         'SSHFP',
#         'IPSECKEY',
#         'RRSIG',
#         'NSEC',
#         'DNSKEY',
#         'DHCID',
#         'NSEC3',
#         'NSEC3PARAM',
#         'TLSA',
#         'HIP',
#         'CDS',
#         'CDNSKEY',
#         'CSYNC',
#         'SPF',
#         'UNSPEC',
#         'EUI48',
#         'EUI64',
#         'TKEY',
#         'TSIG',
#         'IXFR',
#         'AXFR',
#         'MAILB',
#         'MAILA',
#         'ANY',
#         'URI',
#         'CAA',
#         'TA',
#         'DLV',
#     ]
    
#     for a in ids:
#         try:
#             answers = dns.resolver.query(domain, a)
#             for rdata in answers:
#                 print(a, ':', rdata.to_text())
    
#         except Exception as e:
#             print(e)  # or pass

