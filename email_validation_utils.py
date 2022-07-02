from asyncio import constants
import datetime
import response
import constant
import asyncio
import aiodns
import logging
import re
import smtplib
import socket

# import threading
import collections.abc as abc
from constant import Reason, role_key,find_role
import sys
# get the start datetime
st = datetime.datetime.now()

#email pattren regular expresion.
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
    '''
    Caching the result in MX_DNS_CACHE to improve performance.
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
    '''
    check the syntax of email is valid or invalid.
    '''
    email_flag = False
    res_data = None
    if "@" in email:
        if re.match(EMAIL_REGEX, email):
            email_flag = True
        else:
            res_data = response.create_response(email=email,status_code=constant.Status.UNDELIVERABLE.value,reason=constant.Reason.INVALID_EMAIL.value)
    else:
        res_data = {
            "email": f"{email}",
            "status": f"{constant.Status.UNDELIVERABLE.value}",
            "reason": f"{constant.Reason.INVALID_EMAIL.value}"
        }
    return email_flag , res_data 


async def _verify_email(email, timeout=None, verify=True):
    '''
    Validate email by syntax check, domain check and handler check.
    '''
    res_data = None
    is_valid_syntax, res_data = await syntax_check(email)
    if is_valid_syntax:
        if verify:
            mx_hosts = await get_mx_hosts(email)
            if mx_hosts is None:
                res_data = response.create_response(
                email=email,
                status_code= constant.Status.UNKNOWN.value,
                reason=constant.Reason.UNKNOWN.value,
                record=None,
                provider = 'other',
                role='no',
                ttl ='',
                priority =''
            )
                return False,res_data
            else:
                res_data = await handler_verify(mx_hosts, email, timeout)
                return True, res_data
    else:
        return False , res_data

def verify_email(emails, timeout=None, verify=True, debug=False):
    if debug:
        logger = logging.getLogger('verify_email')
        logger.setLevel(logging.DEBUG)
    res_data = None
    if not is_list(emails):
        emails = [emails]
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()

    for email in emails:
        resp,res_data = loop.run_until_complete(_verify_email(email, timeout, verify))
    return resp, res_data

async def verify_email_async(emails, timeout=None, verify=True, debug=False):
    if debug:
        logger = logging.getLogger('verify_email')
        logger.setLevel(logging.DEBUG)
    result = None
    if not is_list(emails):
        emails = [emails]


    for email in emails:
        # result.append(await _verify_email(email, timeout, verify))
        result = await _verify_email(email, timeout, verify)

    return result #if len(result) > 1 else result[0]

async def network_calls(mx, email, timeout=20):
    res_data = None
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
            res_data = response.create_response(
                email=email,
                status_code= constant.Status.RISKY.value if response.decide_reason(_) == constant.Reason.LOW_DELIVERABILITY.value else constant.Status.UNDELIVERABLE.value,
                reason=response.decide_reason(_),
                record=mx.host,
                provider = response.decide_provider(str(mx.host).lower()),
                role=find_role(email,role_key=role_key),
                ttl = mx.ttl,
                priority = mx.priority
            )
        if status >= 200 and status <= 250:

            res_data = response.create_response(
                    email=email,
                    status_code= constant.Status.RISKY.value if response.decide_reason(_) == constant.Reason.LOW_DELIVERABILITY.value else constant.Status.DELIVERABILTY.value,
                    reason=response.decide_reason(_),
                    record=mx.host,
                    provider = response.decide_provider(str(mx).lower()),
                    role=find_role(email,role_key=role_key),
                    ttl = mx.ttl,
                    priority = mx.priority
                )
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
    return result, res_data



# response_data_list = []

# for item in ['sam@libertyvideos.net',"engr.tanveersultan53","engr.tanveersultan53@gmail.com","engr.tanveersultan53@gmail.com"]:
#     res , response_data = verify_email(item)
#     response_data_list.append(response_data)

# print(response_data_list)



