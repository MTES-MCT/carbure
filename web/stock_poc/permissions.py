from core.permissions import UserRightsFactory

# POC: any authenticated user with rights on the selected entity can use the feature.
HasStockPocRights = UserRightsFactory()
