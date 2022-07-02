
import json


def create_response(email=None,status_code=None,reason=None,disposable=None,record=None,role="no",provider=None,ttl=None,priority=None):
    return {
    "email": email,
    "status": status_code,
    "reason": reason,
    "domain": {
        "name": email.split("@")[-1] if email  else "",
        "acceptAll": "yes" if email.split("@")[-1] != "gmail.com" else "no",
        "disposable": "yes" if disposable else "no",
        "free": "yes" if email.split("@")[-1] == "gmail.com" else "no"
    },
    "account": {
        "role": role,
        "disabled": "unknown",
        "fullMailbox": "unknown"
    },
    "dns": {
        "type": "MX",
        "record": record if record else "",
        'ttl':ttl,
        'priority':priority

    },
    "provider": provider if provider else "Other"
}


def decide_reason(_):
    import codecs
    if _.decode("utf-8").endswith("gsmtp") and "The email account that you tried to reach does not exist." not in codecs.decode(_, 'UTF-8') and "at your service" not in codecs.decode(_, 'UTF-8'):
        return "accepted_email"
    else:
        if 'Recipient ok' in codecs.decode(_,'UTF-8'):
            return 'low_deliverability'

        if codecs.decode(_, 'UTF-8').endswith("Ok"):
            return "low_deliverability"
        else:
            if "The email account that you tried to reach does not exist." in codecs.decode(_, 'UTF-8'):
                return "rejected_email"
            elif "Service unavailable" in codecs.decode(_, 'UTF-8'):
                return "accepted_email"
            else:
                return codecs.decode(_, 'UTF-8')


def decide_provider(host):
    print(host)
    if 'google' in host:
        return 'google.com'
    elif 'outlook' in host:
        return 'outlook.com'
    else:
        return "other"
