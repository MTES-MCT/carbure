import { api as apiFetch } from "common/services/api-fetch"
import { UserRole } from "common/types"

export function requestAccess(entity_id: number, role: UserRole, comment = "") {
  return apiFetch.POST("/user/request-access", {
    body: { entity_id, role, comment },
  })
}

export function revokeMyself(entity_id: number) {
  return apiFetch.POST("/user/revoke-access", { body: { entity_id } })
}

export function requestEmailChange(new_email: string, password: string) {
  return (apiFetch as any).POST("/auth/request-email-change/", {
    body: { new_email, password },
  })
}

export function confirmEmailChange(new_email: string, otp_token: string) {
  return (apiFetch as any).POST("/auth/confirm-email-change/", {
    body: { new_email, otp_token },
  })
}

export function requestPasswordChange(
  current_password: string,
  new_password: string,
  confirm_new_password: string
) {
  return (apiFetch as any).POST("/auth/request-password-change/", {
    body: { current_password, new_password, confirm_new_password },
  })
}
