import { lot } from "transaction-details/__test__/data"
import { DeliveryType, LotList, LotSummary, Snapshot } from "transactions/types"

export const emptySnapshot: Snapshot = {
  lots: {
    draft: 0,
    draft_imported: 0,
    draft_stocks: 0,
    in_total: 0,
    in_pending: 0,
    in_tofix: 0,
    stock: 0,
    stock_total: 0,
    out_total: 0,
    out_pending: 0,
    out_tofix: 0,
  },
}
export const snapshot: Snapshot = {
  lots: {
    draft_imported: 30,
    draft_stocks: 0,
    draft: 30,
    in_total: 20,
    in_pending: 0,
    in_tofix: 0,
    stock: 0,
    stock_total: 0,
    out_total: 10,
    out_pending: 0,
    out_tofix: 0,
  },
}

export const emptyLots: LotList = {
  lots: [],
  errors: [],
  ids: [],
  from: 0,
  returned: 0,
  total: 0,
  total_deadline: 0,
  total_errors: 0,
}

export const lots: LotList = {
  lots: [lot],
  errors: [],
  ids: [lot.id],
  from: 0,
  returned: 1,
  total: 1,
  total_deadline: 0,
  total_errors: 0,
}

export const lotSummary: LotSummary = {
  count: 2,
  total_volume: 24690,
  total_weight: 24690,
  total_lhv_amount: 24690,
  in: [
    {
      supplier: "ROQUETTE",
      delivery_type: DeliveryType.Blending,
      biofuel_code: "ETH",
      volume_sum: 12345,
      weight_sum: 12345,
      lhv_amount_sum: 12345,
      avg_ghg_reduction: 76.15,
      total: 1,
      pending: 1,
    },
  ],
  out: [
    {
      client: "TERF",
      delivery_type: DeliveryType.Processing,
      biofuel_code: "ETH",
      volume_sum: 12345,
      weight_sum: 12345,
      lhv_amount_sum: 12345,
      avg_ghg_reduction: 78.57,
      total: 1,
      pending: 0,
    },
  ],
}

export function getFilter(field: string) {
  switch (field) {
    case "feedstocks":
      return [{ value: "COLZA", label: "Colza" }]
    case "biofuels":
      return [{ value: "EMHV", label: "EMHV" }]
    case "periods":
      return [{ value: 202001, label: "2020-01" }]
    case "countries_of_origin":
      return [{ value: "FR", label: "France" }]
    case "production_sites":
      return [{ value: "Test Production Site", label: "Test Production Site" }]
    case "delivery_sites":
      return [{ value: "Test Delivery Site", label: "Test Delivery Site" }]
    case "clients":
      return [{ value: "Opérateur Test", label: "Opérateur Test" }]
    case "suppliers":
      return [
        { value: "Producteur Test", label: "Producteur Test" },
        { value: "Trader Test", label: "Trader Test" },
      ]
  }
}
