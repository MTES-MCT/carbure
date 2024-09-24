import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"

export const okLogin = http.post("/api/auth/login", () => {
  return HttpResponse.json({ status: "success" })
})

export const okOtp = http.post("/api/auth/request-otp", () => {
  return HttpResponse.json({ status: "success" })
})

export const okRequestPasswordReset = http.post(
  "api/auth/request-password-reset",
  () => {
    return HttpResponse.json({ status: "success" })
  }
)

export const okRegisterPending = http.post("api/auth/register", () => {
  return HttpResponse.json({ status: "success" })
})

export const okRequestAcivationLink = http.post(
  "api/auth/request-activation-link",
  () => {
    return HttpResponse.json({ status: "success" })
  }
)

export default setupServer(
  okSettings,
  okLogin,
  okOtp,
  okRequestPasswordReset,
  okRegisterPending,
  okRequestAcivationLink
)
