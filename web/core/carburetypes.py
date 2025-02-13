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
    YEAR_LOCKED = "YEAR_LOCKED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    ENTITY_NOT_ALLOWED = "ENTITY_NOT_ALLOWED"
    NOT_FOUND = "NOT_FOUND"


class CarbureMLGHGErrors:
    EEC_ANORMAL_LOW = "EEC_ANORMAL_LOW"
    EEC_ANORMAL_HIGH = "EEC_ANORMAL_HIGH"
    EP_ANORMAL_LOW = "EP_ANORMAL_LOW"
    EP_ANORMAL_HIGH = "EP_ANORMAL_HIGH"
    ETD_ANORMAL_HIGH = "ETD_ANORMAL_HIGH"
    ETD_NO_EU_TOO_LOW = "ETD_NO_EU_TOO_LOW"
    ETD_EU_DEFAULT_VALUE = "ETD_EU_DEFAULT_VALUE"


class CarbureCertificatesErrors:
    REJECTED_SUPPLIER_CERTIFICATE = "Your supplier certificate has been rejected by the DGEC"
    UNKNOWN_PRODSITE_CERT = "UNKNOWN_PRODSITE_CERT"
    EXPIRED_PRODSITE_CERT = "EXPIRED_PRODSITE_CERT"
    NO_SUPPLIER_CERT = "NO_SUPPLIER_CERT"
    UNKNOWN_SUPPLIER_CERT = "UNKNOWN_SUPPLIER_CERT"
    EXPIRED_SUPPLIER_CERT = "EXPIRED_SUPPLIER_CERT"
    MISSING_REF_DBL_COUNTING = "MISSING_REF_DBL_COUNTING"
    UNKNOWN_DOUBLE_COUNTING_CERTIFICATE = "UNKNOWN_DOUBLE_COUNTING_CERTIFICATE"
    EXPIRED_DOUBLE_COUNTING_CERTIFICATE = "EXPIRED_DOUBLE_COUNTING_CERTIFICATE"
    INVALID_DOUBLE_COUNTING_CERTIFICATE = "INVALID_DOUBLE_COUNTING_CERTIFICATE"
    MISSING_SUPPLIER_CERTIFICATE = "MISSING_SUPPLIER_CERTIFICATE"
    MISSING_VENDOR_CERTIFICATE = "MISSING_VENDOR_CERTIFICATE"


class CarbureSanityCheckErrors:
    GHG_REDUC_SUP_100 = "GHG_REDUC_SUP_100"
    GHG_REDUC_SUP_99 = "GHG_REDUC_SUP_99"
    GHG_REDUC_INF_50 = "GHG_REDUC_INF_50"
    GHG_ETD_0 = "GHG_ETD_0"
    GHG_EP_0 = "GHG_EP_0"
    GHG_EL_NEG = "GHG_EL_NEG"
    GHG_EEC_0 = "GHG_EEC_0"
    GHG_REDUC_INF_60 = "GHG_REDUC_INF_60"
    GHG_REDUC_INF_65 = "GHG_REDUC_INF_65"
    EEC_WITH_RESIDUE = "EEC_WITH_RESIDUE"

    MAC_BC_WRONG = "MAC_BC_WRONG"
    MAC_NOT_EFPE = "MAC_NOT_EFPE"
    VOLUME_FAIBLE = "VOLUME_FAIBLE"
    PROVENANCE_MP = "PROVENANCE_MP"
    DEPRECATED_MP = "DEPRECATED_MP"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    MISSING_REF_DBL_COUNTING = "MISSING_REF_DBL_COUNTING"
    MP_NOT_CONFIGURED = "MP_NOT_CONFIGURED"
    BC_NOT_CONFIGURED = "BC_NOT_CONFIGURED"
    DEPOT_NOT_CONFIGURED = "DEPOT_NOT_CONFIGURED"
    DELIVERY_IN_THE_FUTURE = "DELIVERY_IN_THE_FUTURE"

    MISSING_VOLUME = "MISSING_VOLUME"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    UNKNOWN_PRODUCTION_SITE = "UNKNOWN_PRODUCTION_SITE"
    MISSING_PRODUCTION_SITE_COMDATE = "MISSING_PRODUCTION_SITE_COMDATE"
    MISSING_TRANSPORT_DOCUMENT_REFERENCE = "MISSING_TRANSPORT_DOCUMENT_REFERENCE"
    MISSING_CARBURE_DELIVERY_SITE = "MISSING_CARBURE_DELIVERY_SITE"
    MISSING_CARBURE_CLIENT = "MISSING_CARBURE_CLIENT"
    YEAR_LOCKED = "YEAR_LOCKED"
    MISSING_DELIVERY_DATE = "MISSING_DELIVERY_DATE"
    WRONG_DELIVERY_DATE = "WRONG_DELIVERY_DATE"
    MISSING_DELIVERY_SITE_COUNTRY = "MISSING_DELIVERY_SITE_COUNTRY"
    MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN = "MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN"

    DECLARATION_ALREADY_VALIDATED = "DECLARATION_ALREADY_VALIDATED"
    DELIVERY_DATE_VALIDITY = "DELIVERY_DATE_VALIDITY"


class CarbureStockErrors:
    NOT_ENOUGH_VOLUME_LEFT = "NOT_ENOUGH_VOLUME_LEFT"


class CarbureUnit:
    KILOGRAM = "kg"
    LITER = "l"
    LHV = "mj"
