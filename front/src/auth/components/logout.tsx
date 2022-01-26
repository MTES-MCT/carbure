import { useQuery } from "common-v2/hooks/async"
import { invalidate } from "common-v2/hooks/invalidate"
import { Navigate } from "react-router-dom"
import * as api from "../api"

export const Logout = () => {
  useQuery(api.logout, {
    key: "logout",
    params: [],
    onSuccess: () => invalidate("user-settings"),
  })

  return <Navigate to="/" />
}
