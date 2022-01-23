import { UserRight, UserRightRequest } from "carbure/types"

export type ProductionCertificate = {
  certificate_id: string
  holder: string
  type: "2BS" | "ISCC" | "REDCERT" | "SN"
}

export interface EntityRights {
  rights: UserRight[]
  requests: UserRightRequest[]
}
