from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def was_issued_for(self, user, token):
        """True when the token was signed for this user, including after it expired."""
        if not (user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
            timestamp = base36_to_int(ts_b36)
        except ValueError:
            return False

        expected = self._make_token_with_timestamp(user, timestamp, self.secret)

        return constant_time_compare(expected, token)

    def _make_hash_value(self, user, timestamp):
        # is_active invalidates the link once the account is activated.
        # password invalidates previously issued links when an invited user's secret is rotated.
        return "".join([str(user.pk), str(timestamp), str(user.email), str(user.is_active), str(user.password)])


class PasswordResetOneTimeTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Bind token validity to password hash so it is invalidated immediately after a successful reset.
        login_timestamp = ""
        if user.last_login is not None:
            login_timestamp = str(user.last_login.replace(microsecond=0, tzinfo=None))

        return str(user.pk) + str(user.password) + login_timestamp + str(timestamp) + str(user.email)


account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetOneTimeTokenGenerator()
