import { UserRight, UserRightRequest } from "carbure/types"

export interface EntityRights {
  rights: UserRight[]
  requests: UserRightRequest[]
}
