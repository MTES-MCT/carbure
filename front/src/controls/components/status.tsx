import { useMatch } from "react-router-dom"
import { AdminStatus } from "../types"

export function useStatus() {
  const match = useMatch("/org/:entity/controls/:year/:status/*") // prettier-ignore
  return (match?.params.status ?? "unknown") as AdminStatus
}
