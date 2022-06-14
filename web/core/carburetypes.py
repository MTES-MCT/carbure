class Carbure:
    SUCCESS = "success"
    ERROR = "error"

class CarbureError:
    INVALID_REGISTRATION_FORM = "Invalid registration form"
    INVALID_LOGIN_CREDENTIALS = "Invalid login or password"
    ACCOUNT_NOT_ACTIVATED = "Account not activated"
    OTP_EXPIRED_CODE = "OTP Code Expired"
    OTP_INVALID_CODE = "OTP Code Invalid"
    OTP_RATE_LIMITED = "OTP Rate Limited"
    OTP_UNKNOWN_ERROR = "OTP Unknown Error"
    OTP_INVALID_FORM = "OTP Invalid Form"
    PASSWORD_RESET_USER_NOT_FOUND = "User not found"
    PASSWORD_RESET_INVALID_FORM = "Password reset invalid form"
    PASSWORD_RESET_MISMATCH = "Passwords do not match"
    ACTIVATION_LINK_ERROR = "Could not send activation link" 
    ACTIVATION_LINK_INVALID_FORM = "Activation link invalid form"
    ACTIVATION_COULD_NOT_ACTIVATE_USER = "Could not activate user account"
    CANCEL_ACCEPT_NOT_ALLOWED = "CANCEL_ACCEPT_NOT_ALLOWED"
    