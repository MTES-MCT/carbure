from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# This throttle is used to limit the number of emails sent to a user
class UserEmailThrottle(UserRateThrottle):
    scope = "10/day"


class AnonEmailThrottle(AnonRateThrottle):
    scope = "10/day"
