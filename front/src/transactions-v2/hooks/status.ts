import { useMatch } from "react-router-dom"
import { Status } from "../types"

export function useStatus() {
  const match = useMatch<"status">("/org/:entity/transactions-v2/:status/*")
  return (match?.params.status ?? "unknown") as Status
}

export default useStatus
