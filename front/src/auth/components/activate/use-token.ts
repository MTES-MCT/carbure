import { useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"

export function useToken() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const uidb64 = searchParams.get("uidb64") ?? undefined
  const token = searchParams.get("token") ?? undefined

  useEffect(() => {
    if (uidb64 === undefined || token === undefined) {
      navigate(ROUTE_URLS.HOME)
    }
  }, [uidb64, token, navigate])

  return { uidb64, token }
}
