import { admin, entityRight } from "carbure/__test__/data"
import { rest } from "msw"
import { setupServer } from "msw/node"

import {
	okTranslations,
	okFieldsTranslations,
	okErrorsTranslations,
} from "carbure/__test__/api"

import { getFilter } from "transactions/__test__/data"
import { lotSummary } from "./data"
import { lots } from "./data"

export const okAdminSettings = rest.get("/api/user", (req, res, ctx) => {
	return res(
		ctx.json({
			status: "success",
			data: {
				email: "admin@test.com",
				rights: [{ ...entityRight, entity: admin }],
				requests: [{ ...entityRight, entity: admin }],
			},
		})
	)
})

export const okLotsSummary = rest.get(
	"/api/transactions/admin/lots/summary",
	(req, res, ctx) => {
		return res(ctx.json({ status: "success", data: lotSummary }))
	}
)

export const okFilters = rest.get(
	"/api/transactions/admin/lots/filters",
	(req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
				data: getFilter(req.url.searchParams.get("field") ?? ""),
			})
		)
	}
)

export const okSnapshot = rest.get(
	"/api/transactions/admin/snapshot",
	(req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
				data: {
					lots: {
						alerts: 0,
						lots: 0,
						stocks: 0,
					},
				},
			})
		)
	}
)

export const okLots = rest.get(
	"/api/transactions/admin/lots",
	(req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
				data: {
					lots: lots,
					from: 0,
					returned: 3,
					total: 3,
					total_errors: 0,
					total_deadline: 0,
					errors: {},
				},
			})
		)
	}
)

export const okStocks = rest.get(
	"/api/transactions/admin/stocks",
	(req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
			})
		)
	}
)

export const okYears = rest.get(
	"/api/transactions/admin/years",
	(req, res, ctx) => {
		return res(
			ctx.json({
				status: "success",
				data: [],
			})
		)
	}
)

export default setupServer(
	okSnapshot,
	okLots,
	okLotsSummary,
	okTranslations,
	okErrorsTranslations,
	okFieldsTranslations,
	okFilters,
	okYears,
	okSnapshot,
	okStocks,
	okAdminSettings
)
