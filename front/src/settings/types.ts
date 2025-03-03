import { UserRight, UserRightRequest } from "common/types"

export interface EntityRights {
  rights: UserRight[]
  requests: UserRightRequest[]
}
