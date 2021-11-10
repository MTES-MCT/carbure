import { useMatch } from "react-router-dom"

export type Status = "DRAFT" | "IN" | "STOCK" | "OUT" | "ADMIN" | "UNKNOWN"
const URL_TO_STATUS: Record<string, Status> = {
  draft: "DRAFT",
  in: "IN",
  stock: "STOCK",
  out: "OUT",
  admin: "ADMIN",
  unknown: "UNKNOWN",
}

export function useStatus() {
  const match = useMatch<"status">("/org/:entity/transactions-v2/:status")
  const urlStatus = match?.params.status as keyof typeof URL_TO_STATUS ?? "unknown" // prettier-ignore
  return URL_TO_STATUS[urlStatus]
}

export default useStatus
