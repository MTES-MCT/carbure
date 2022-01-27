import { useNavigate } from "react-router-dom"
import { useQuery } from "common-v2/hooks/async"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { invalidate } from "common-v2/hooks/invalidate"
import * as api from "../api"

export const Logout = () => {
  const navigate = useNavigate()

  useQuery(api.logout, {
    key: "logout",
    params: [],
    onSuccess: () => {
      invalidate("user-settings")
      navigate("/")
    }
  })

  return <LoaderOverlay />
}
