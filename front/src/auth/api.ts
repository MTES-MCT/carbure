import { api } from "common/services/api"

export function register(
  email: string,
  name: string,
  password1: string,
  password2: string
) {
  return api.post("/auth/register", { email, name, password1, password2 })
}

export function login(username: string, password: string) {
  return api.post("auth/login", { username, password })
}

export function logout() {
  return api.post("auth/logout")
}

export function requestOTP() {
  return api.post("auth/request-otp")
}

export function verifyOTP(otp_token: string) {
  return api.post("auth/verify-otp", { otp_token })
}

export function requestResetPassword(username: string) {
  return api.post("auth/request-password-reset", { username })
}

export function resetPassword(
  uidb64: string | undefined,
  token: string | undefined,
  password1: string,
  password2: string
) {
  if (uidb64 === undefined || token === undefined) {
    throw new Error("Missing token for password reset")
  }

  return api.post("auth/reset-password", {
    uidb64,
    token,
    password1,
    password2,
  })
}

export function requestActivateAccount(email: string) {
  return api.post("auth/request-activation-link", { email })
}

export function activateAccount(
  uidb64: string | undefined,
  token: string | undefined
) {
  if (uidb64 === undefined || token === undefined) {
    throw new Error("Missing token for account activation")
  }

  return api.post("auth/activate", { uidb64, token })
}
