

import enum


role_key =["abuse",
"accounting",
"accounts",
"admin",
"administration",
"administrator",
"admissions",
"ads",
"all",
"answers",
"anti-spam",
"antispam",
"asdf",
"billing",
"ceo",
"comments",
"compliance",
"contact",
"contactus",
"customer",
"customercare",
"customerservice",
"database",
"decliend",
"decline",
"declined",
"denied",
"designer",
"devnull",
"director",
"dns",
"email",
"employment",
"enquiries",
"everyone",
"fbl",
"feedback",
"finance",
"ftp",
"general",
"hello",
"helpdesk",
"home",
"hostmaster",
"hr",
"info",
"information",
"inoc",
"investorrelations",
"ispfeedback",
"ispsupport",
"jobs",
"lawyer",
"lawyers",
"legal",
"list",
"list-request",
"mail",
"mailbox",
"mail-daemon",
"maildaemon",
"mail-deamon",
"manager",
"managers",
"marketing",
"me",
"media",
"mediarelations",
"mkt",
"news",
"noc",
"noreplies",
"no-reply",
"noreply",
"noemail",
"nospam",
"nothanks",
"null",
"office",
"operations",
"orders",
"phish",
"phishing",
"post",
"postbox",
"postmaster",
"prepress",
"president",
"press",
"privacy",
"purchasing",
"qwer",
"qwert",
"qwerty",
"reception",
"refuse",
"refused",
"registrar",
"remove",
"request",
"reservations",
"returns",
"root",
"sales",
"secretary",
"security",
"service",
"services",
"shop",
"spam",
"staff",
"studio",
"subscribe",
"support",
"sysadmin",
"tech",
"undisclosed-recipients",
"unsubscribe",
"usenet",
"users",
"uucp",
"web",
"webmaster",
"welcome",
"www"]


def find_role(email,role_key):
    role_list = []
    for item in role_key:
        if item in email:
            role_list.append(item)
        else:
            role = None
    return role_list    

em = "admin@gmail.com"



class Status(enum.Enum):
    DELIVERABILTY = "deliverable"
    RISKY = "risky"
    UNDELIVERABLE  ="undeliverable"
    UNKNOWN = "unknown"


class Reason(enum.Enum):
    LOW_DELIVERABILITY = "low_deliverability"
    INVALID_EMAIL = "invalid_email"
    REJECTED_EMAIL = "rejected_email"
    UNKNOWN = "unknown"