import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include activation state so the token becomes invalid right after first successful activation.
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.email) + six.text_type(user.is_active)


account_activation_token = AccountActivationTokenGenerator()
