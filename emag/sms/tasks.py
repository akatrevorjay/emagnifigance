
from django_twilio.client import twilio_client


def print_phone_numbers():
    for number in twilio_client.phone_numbers.iter():
        print number.friendly_name


def send_sms(recipient, body, sender):
    message = twilio_client.sms.messages.create(
        to=str(recipient),
        from_=str(sender),
        body=str(body),
    )
    return message
