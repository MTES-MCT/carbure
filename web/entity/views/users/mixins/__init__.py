from .change_role import ChangeRoleActionMixin
from .entity_rights import EntityRightsRequestsActionMixin
from .grant_access import GrantAccessActionMixin
from .invite_user import InviteUserActionMixin
from .revoke_access import RevokeUserActionMixin
from .rights_requests import RightsRequestsActionMixin
from .update_right_request import UpdateRightsRequestsActionMixin
from .update_user_role import UpdatUserRoleActionMixin


class UserActionMixin(
    ChangeRoleActionMixin,
    EntityRightsRequestsActionMixin,
    GrantAccessActionMixin,
    InviteUserActionMixin,
    RevokeUserActionMixin,
    RightsRequestsActionMixin,
    UpdateRightsRequestsActionMixin,
    UpdatUserRoleActionMixin,
):
    pass
