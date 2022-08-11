import { rest } from "msw"
import { setupServer } from "msw/node"
import {
  okSettings
} from "settings/__test__/api"


export const okLogin = rest.post("/api/auth/login", (req, res, ctx) => {
  return res(ctx.json({ status: "success" }))
})

export default setupServer(
  okSettings

)
