from .activate import ActivateAccountAction
from .activate_profile import ActivateProfileAction
from .change_email import ChangeEmailActionMixin
from .change_password import ChangePasswordActionMixin
from .login import UserLoginAction
from .logout import UserLogoutAction
from .register import UserCreationAction
from .request_activation_link import UserResendActivationLinkAction
from .request_otp import RequestOTPAction
from .request_password_reset import RequestPasswordResetAction
from .reset_password import ResetPasswordAction
from .verify_otp import VerifyOTPAction


class AuthActionMixin(
    ActivateAccountAction,
    ActivateProfileAction,
    ChangeEmailActionMixin,
    ChangePasswordActionMixin,
    UserLoginAction,
    UserLogoutAction,
    UserCreationAction,
    UserResendActivationLinkAction,
    RequestOTPAction,
    VerifyOTPAction,
    RequestPasswordResetAction,
    ResetPasswordAction,
):
    pass
