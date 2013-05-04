
import mongoengine as m
import re


class PhoneNumberField(m.StringField):
    REGEX = re.compile(r'^\+?(\d*)[- ]?(\d{3})[- ]?(\d{3})[- ]?(\d{4})$',
                       re.IGNORECASE)

    def validate(self, value):
        if not PhoneNumberField.REGEX.match(value):
            self.error('Invalid Phone Number: %s' % value)
        super(PhoneNumberField, self).validate(value)

    @classmethod
    def clean(cls, phone):
        phone = unicode(phone)
        m = PhoneNumberField.REGEX.match(phone)
        if not m:
            raise ValueError("Phone number cannot be matched in: %s" % phone)
        m = list(m.groups())
        if not m[0]:
            m[0] = '1'
        return ''.join(m)

    #def to_python(self, value):
    #    return super(PhoneNumberField, self).to_python(value)

    def to_mongo(self, value):
        value = self.clean(value)
        return super(PhoneNumberField, self).to_mongo(value)
