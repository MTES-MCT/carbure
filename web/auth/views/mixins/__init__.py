from .activate import ActivateAccountAction
from .login import UserLoginAction
from .logout import UserLogoutAction
from .register import UserCreationAction
from .request_activation_link import UserResendActivationLinkAction
from .request_otp import RequestOTPAction
from .verify_otp import VerifyOTPAction
from .request_password_reset import RequestPasswordResetAction
from .reset_password import ResetPasswordAction


class AuthActionMixin(
    ActivateAccountAction,
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
