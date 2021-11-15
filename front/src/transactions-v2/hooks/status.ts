import { useMatch } from "react-router-dom"
import { Status } from '../types'

const URL_TO_STATUS: Record<string, Status> = {
  drafts: "DRAFTS",
  in: "IN",
  stocks: "STOCKS",
  out: "OUT",
  admin: "ADMIN",
  unknown: "UNKNOWN",
}

export function useStatus() {
  const match = useMatch<"status">("/org/:entity/transactions-v2/:status/*")
  const urlStatus = match?.params.status as keyof typeof URL_TO_STATUS ?? "unknown" // prettier-ignore
  return URL_TO_STATUS[urlStatus]
}

export default useStatus
