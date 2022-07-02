import datetime
from itertools import count
import json
from textwrap import indent
import response
import constant

# get the start datetime
st = datetime.datetime.now()
import asyncio
import aiodns
import logging
import re
import smtplib
import socket
# import threading
import collections.abc as abc
from constant import role_key,find_role
import sys
# from constant import find_role

EMAIL_REGEX = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
MX_DNS_CACHE = {}
MX_CHECK_CACHE = {}

data = []

# Set up logging on module load and avoid adding 'ch' or 'logger' to module
# namespace.  We could assign the logger to a module level name, but it is only
# used by two functions, and this approach demonstrates using the 'logging'
# namespace to retrieve arbitrary loggers.

def setup_module_logger(name):
    """Set up module level logging with formatting"""
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    # Really should not be configuring formats in a library, see
    # https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


setup_module_logger('verify_email')


def is_list(obj):
    return isinstance(obj, abc.Sequence) and not isinstance(obj, str)

async def get_mx_ip(hostname):
    '''
        Get MX record by hostname.
    '''
    if hostname not in MX_DNS_CACHE:
        try:
            resolver = aiodns.DNSResolver()
            MX_DNS_CACHE[hostname]= await resolver.query(hostname, 'MX')
            print(MX_DNS_CACHE[hostname])
            
            
        except aiodns.error.DNSError as e:
            MX_DNS_CACHE[hostname] = None
    return MX_DNS_CACHE[hostname]


async def get_mx_hosts(email):
    '''Caching the result in MX_DNS_CACHE to improve performance.
    '''
    hostname = email[email.find('@') + 1:]
    if hostname in MX_DNS_CACHE:
        mx_hosts = MX_DNS_CACHE[hostname]
        print(mx_hosts,"mx_host")
    else:
        mx_hosts = await get_mx_ip(hostname)
        print(mx_hosts)
    return mx_hosts



async def handler_verify(mx_hosts, email, timeout=None):
    for mx in mx_hosts:
        res = await network_calls(mx, email, timeout)
        print(res)
        if res:
            return res
        return False


async def syntax_check(email):
    flag = False
    if "@" in email:
        if re.match(EMAIL_REGEX, email):
            flag = True
        else:
            data.append(response.create_response(email=email,status_code=constant.Status.UNDELIVERABLE.value,reason=constant.Reason.INVALID_EMAIL.value))
    else:
        data.append({
            "email": f"{email}",
            "status": f"{constant.Status.UNDELIVERABLE.value}",
            "reason": f"{constant.Reason.INVALID_EMAIL.value}"
        })
    return flag


async def _verify_email(email, timeout=None, verify=True):
    '''Validate email by syntax check, domain check and handler check.
    '''
    is_valid_syntax = await syntax_check(email)
    if is_valid_syntax:
        if verify:
            mx_hosts = await get_mx_hosts(email)
            print(mx_hosts)
            if mx_hosts is None:
                return False
            else:
                return await handler_verify(mx_hosts, email, timeout)
    else:
        return False

def verify_email(emails, timeout=None, verify=True, debug=False):
    if debug:
        logger = logging.getLogger('verify_email')
        logger.setLevel(logging.DEBUG)
    result = []
    if not is_list(emails):
        emails = [emails]
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()

    for email in emails:
        resp = loop.run_until_complete(_verify_email(email, timeout, verify))
        result.append(resp)

    return result if len(result) > 1 else result[0]

async def verify_email_async(emails, timeout=None, verify=True, debug=False):
    if debug:
        logger = logging.getLogger('verify_email')
        logger.setLevel(logging.DEBUG)
    result = []
    if not is_list(emails):
        emails = [emails]


    for email in emails:
        result.append(await _verify_email(email, timeout, verify))

    return result if len(result) > 1 else result[0]

async def network_calls(mx, email, timeout=20):
    logger = logging.getLogger('verify_email')
    result = False
    try:
        smtp = smtplib.SMTP(mx.host, timeout=timeout)
        status, _ = smtp.ehlo()
        print(_,"message")
        print(status,"status code")
        if status >= 400:
            smtp.quit()
            logger.debug(f'{mx} answer: {status} - {_}\n')
            return False
        smtp.mail('')
        status, _ = smtp.rcpt(email)
        if status >= 400:
            logger.debug(f'{mx} answer: {status} - {_}\n')
            result = False
            data.append(
                response.create_response(
                email=email,
                status_code= constant.Status.RISKY.value if response.decide_reason(_) == constant.Reason.LOW_DELIVERABILITY.value else constant.Status.UNDELIVERABLE.value,
                reason=response.decide_reason(_),
                record={mx.host},
                provider = response.decide_provider(str(mx.host).lower()),
                role=find_role(email,role_key=role_key),
                ttl = mx.ttl,
                priority = mx.priority
            ))  
        #     data.append({
        #     "email":email,
        #     "email_host":str(mx.host),
        #     "status_code":"risky" if response.decide_reason(_) == "low_deliverability" else constant.Status.UNDELIVERABLE.value ,
        #     "reason": response.decide_reason(_) ,
        #     "account":{
        #         "role": find_role(email,role_key=role_key),
        #         "disabled":"unknown",
        #         "fullMailbox":"unknown"
        #     },
        #     "dns":{
        #         "type":"MX",
        #         "record":f"{mx.host}",
        #         'ttl':mx.ttl,
        #         'priority':mx.priority,
        #     },
        #     "provider": response.decide_provider(str(mx.host).lower())
        # })
        if status >= 200 and status <= 250:
            data.append(
                response.create_response(
                    email=email,
                    status_code= constant.Status.RISKY.value if response.decide_reason(_) == constant.Reason.LOW_DELIVERABILITY.value else constant.Status.DELIVERABILTY.value,
                    reason=response.decide_reason(_),
                    record={mx.host},
                    provider = response.decide_provider(str(mx).lower()),
                    role=find_role(email,role_key=role_key),
                    ttl = mx.ttl,
                    priority = mx.priority
                ))
            
        #     data.append({
        #     "email":email,
        #     "email_host":str(mx.host),
        #     "status_code":"risky" if response.decide_reason(_) == "low_deliverability" else constant.Status.DELIVERABILTY.value,
        #     "reason": response.decide_reason(_),
        #     "account":{
        #         "role": find_role(email,role_key=role_key),
        #         "disabled":"unknown",
        #         "fullMailbox":"unknown"
        #     },
        #     "dns":{
        #         "type":"MX",
        #         "record":f"{mx.host}",
        #         'ttl':mx.ttl,
        #         'priority':mx.priority,
        #     },
        #     "provider": response.decide_provider(str(mx.host).lower())
        # })
            result = True

        logger.debug(f'{mx} answer: {status} - {_}\n')
        smtp.quit()

    except smtplib.SMTPServerDisconnected:
        logger.debug(f'Server does not permit verify user, {mx} disconnected.\n')
    except smtplib.SMTPConnectError:
        logger.debug(f'Unable to connect to {mx}.\n')
    except socket.timeout as e:
        logger.debug(f'Timeout connecting to server {mx}: {e}.\n')
        return None
    except socket.error as e:
        logger.debug(f'ServerError or socket.error exception raised {e}.\n')
        return None
    return result

def list_of_emails(list_emails=[]):
    count = 0
    for email in ['engr.tanveersultan53@gamil.com']:
        try:
            if count == 20:
                break
            if email:
                verify_email(email)
                count +=1
        except:
            pass
    return data

# file = open('email_data.json', 'wb')
# file.write(json.dumps(data))

# # # get the end datetime
# et = datetime.datetime.now()

# # get execution time
# elapsed_time = et - st
# print('Execution time:', elapsed_time, 'seconds')

# # print(json.dumps(data, indent=4))

# # print(data)


# import json

# class SetEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, set):
#             return list(obj)
#         return json.JSONEncoder.default(self, obj)

# with open('app1.json', 'w', encoding='utf-8') as f:
#     f.write(json.dumps(data,cls=SetEncoder,indent=2))

list_of_emails()