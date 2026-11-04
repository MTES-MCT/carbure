import { useEffect } from "react"
import { useLocation, useNavigate, useSearchParams } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"

export type PasswordResetState = {
  uidb64: string
  token: string
}

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

// The email link still carries the token in the query string.
// The activation screen passes it in router state, so the URL itself does not.
export function usePasswordToken() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const fromQuery = passwordResetState({
    uidb64: searchParams.get("uidb64") ?? undefined,
    token: searchParams.get("token") ?? undefined,
  })
  const credentials = fromQuery ?? passwordResetState(location.state)
  const uidb64 = credentials?.uidb64
  const token = credentials?.token

  useEffect(() => {
    if (uidb64 === undefined || token === undefined) {
      navigate(ROUTE_URLS.AUTH.RESET_PASSWORD_REQUEST, { replace: true })
    }
  }, [uidb64, token, navigate])

  return { uidb64, token }
}

function passwordResetState(state: unknown): PasswordResetState | undefined {
  if (typeof state !== "object" || state === null) return undefined
  const value = state as Partial<PasswordResetState>
  if (!value.uidb64 || !value.token) return undefined
  return { uidb64: value.uidb64, token: value.token }
}
