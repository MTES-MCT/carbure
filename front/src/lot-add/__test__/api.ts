import { lot } from "common/__test__/data"
import { rest } from "msw"

export const okAddLot = rest.post("/api/lots/add", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: lot,
    })
  )
})
