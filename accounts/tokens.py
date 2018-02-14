from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class PasswordResetTokenGenerator1(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return (
            six.text_type(user.pk) + user.password +
            six.text_type(login_timestamp) + six.text_type(timestamp)
        )

password_reset_token = PasswordResetTokenGenerator()
