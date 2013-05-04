
import mongoengine as m
import re


class EnvelopeEmailField(m.StringField):
    ENVELOPE_EMAIL_REGEX = re.compile(
        #r'^"([-0-9A-Z ]+)" <'  # name
        r'^"([^"]+)" <'  # name
        r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?>$', re.IGNORECASE  # domain
    )

    def validate(self, value):
        if not EnvelopeEmailField.ENVELOPE_EMAIL_REGEX.match(value):
            self.error('Invalid Envelope Mail-address: %s' % value)
        super(EnvelopeEmailField, self).validate(value)
