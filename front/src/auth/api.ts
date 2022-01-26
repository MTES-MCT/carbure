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

export function verifyOTP(otp: string) {
  return api.post("/auth/verify-otp", { otp })
}

export function requestPasswordReset(email: string) {
  return api.post("/auth/request-password-reset", { email })
}

export function resetPassword(
  old_password: string,
  password1: string,
  password2: string
) {
  return api.post("/auth/reset-password", {
    old_password,
    password1,
    password2,
  })
}

export function requestActivationLink(email: string) {
  return api.post("/auth/request-activation-link", { email })
}

export function activateAccount(hash: string) {
  return api.post("/auth/activate", { hash })
}
