from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include activation state so the token becomes invalid right after first successful activation.
        return str(user.pk) + str(timestamp) + str(user.email) + str(user.is_active)


class PasswordResetOneTimeTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Bind token validity to password hash so it is invalidated immediately after a successful reset.
        login_timestamp = ""
        if user.last_login is not None:
            login_timestamp = str(user.last_login.replace(microsecond=0, tzinfo=None))

        return str(user.pk) + str(user.password) + login_timestamp + str(timestamp) + str(user.email)


account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetOneTimeTokenGenerator()
