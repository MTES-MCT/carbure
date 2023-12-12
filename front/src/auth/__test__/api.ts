import { rest } from "msw"
import { setupServer } from "msw/node"
import {
  okSettings
} from "settings/__test__/api"


export const okLogin = rest.post("/api/auth/login", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okOtp = rest.post("/api/auth/request-otp", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okRequestPasswordReset = rest.post("api/auth/request-password-reset", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okRegisterPending = rest.post("api/auth/register", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export const okRequestAcivationLink = rest.post("api/auth/request-activation-link", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export default setupServer(
  okSettings,
  okLogin,
  okOtp,
  okRequestPasswordReset,
  okRegisterPending,
  okRequestAcivationLink
)
