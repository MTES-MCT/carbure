import { useMatch } from "react-router-dom"
import { ChargePointStatus } from "./types"

export const useStatus = () => {
  const matchStatus = useMatch("/org/:entity/charge-points/:year/list/:status")

  const status = matchStatus?.params?.status?.toUpperCase() as ChargePointStatus

  return status
}
