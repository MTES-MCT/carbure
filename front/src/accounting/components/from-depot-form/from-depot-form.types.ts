import { apiTypes } from "common/services/api-fetch.types"

// Type of the form part
export type FromDepotFormProps = {
  from_depot?: apiTypes["BalanceDepot"] & {
    available_balance: number
  }
  gesBoundMin?: number
  gesBoundMax?: number
}
