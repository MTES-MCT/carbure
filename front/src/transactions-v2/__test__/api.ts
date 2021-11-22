import { rest } from "msw"
import { setupServer } from "msw/node"

export const okSnapshot = rest.get("/api/snapshot", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        lots: {
          draft: 0,
          in_total: 0,
          in_pending: 0,
          in_tofix: 0,
          stock: 0,
          stock_total: 0,
          out_total: 0,
          out_pending: 0,
          out_tofix: 0,
        },
      },
    })
  )
})

export const okLots = rest.get("/api/lots", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: {
        data: {
          lots: [],
          from: 0,
          returned: 0,
          total: 0,
          total_errors: 0,
          total_deadline: 0,
          errors: {},
        },
      },
    })
  )
})

export const okYears = rest.get("/api/years", (req, res, ctx) => {
  return res(
    ctx.json({
      status: "success",
      data: [],
    })
  )
})

export default setupServer(okSnapshot, okLots, okYears)
