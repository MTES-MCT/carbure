import { http } from "msw"
import { setupServer } from "msw/node"
import { okSettings } from "settings/__test__/api"

export const okLogin = http.post("/api/auth/login", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okOtp = http.post("/api/auth/request-otp", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okRequestPasswordReset = http.post(
  "api/auth/request-password-reset",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success" }))
  }
)

export const okRegisterPending = http.post(
  "api/auth/register",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success" }))
  }
)

export const okRequestAcivationLink = http.post(
  "api/auth/request-activation-link",
  (req, res, ctx) => {
    return res(ctx.json({ status: "success" }))
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
