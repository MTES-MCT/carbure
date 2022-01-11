import { rest } from "msw"
import { lot, lotDetails } from "./data"

export const okLotDetails = rest.get("/api/lots/details", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: lotDetails,
    })
  )
})

export const okUpdateLot = rest.post("/api/lots/update", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: lot,
    })
  )
})
