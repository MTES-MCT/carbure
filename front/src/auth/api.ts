import { api } from "common-v2/services/api"

export function register(email: string, password1: string, password2: string) {
  return api.post("/auth/register", { email, password1, password2 })
}

export function login(email: string, password: string) {
  return api.post("/auth/login", { email, password })
}

export function logout() {
  return api.post("/auth/logout")
}

export function requestOTP() {
  return api.post("/auth/request-otp")
}

export function verifyOTP(otp_token: string) {
  return api.post("/auth/verify-otp", { otp_token })
}

export function requestResetPassword(email: string) {
  return api.post("/auth/request-password-reset", { email })
}

export function resetPassword(
  token: string | null,
  old_password: string,
  password1: string,
  password2: string
) {
  if (token === null) {
    throw new Error("Missing token for password reset")
  }

  return api.post("/auth/reset-password", {
    token,
    old_password,
    password1,
    password2,
  })
}

export function requestActivateAccount(email: string) {
  return api.post("/auth/request-activation-link", { email })
}

export function activateAccount(token: string | null) {
  if (token === null) {
    throw new Error("Token missing for account activation")
  }

  return api.post("/auth/activate", { token })
}
