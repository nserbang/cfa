import re
from django import template

register = template.Library()

pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


@register.filter
def format_email(value):
    emails = pattern.findall(value)
    print(emails)
    if emails:
        for email in emails:
            rep = email
            rep = rep.replace("@", "[at]")
            rep = rep.replace(".", "[dot]")
            value = value.replace(email, rep)
            print(rep)
        print(value)
    return value
