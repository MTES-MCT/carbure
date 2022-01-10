import { Snapshot, GenericError, LotDetails, Lots, DeliveryStatus } from "common/types"
import { country, lot, producer, operator, trader } from "common/__test__/data"

export const emptySnapshot = {
  years: [2020, 2019],
  lots: {
    draft: 0,
    validated: 0,
    tofix: 0,
    accepted: 0,
  },
  filters: [
    'matieres_premieres',
    'biocarburants',
    'periods',
    'production_sites',
    'countries_of_origin',
    'delivery_sites',
    'clients',
  ],
  depots: [],
}

export const snapshot = {
  years: [2020, 2019],
  lots: {
    draft: 40,
    validated: 30,
    tofix: 20,
    accepted: 10,
  },
  filters: [
    'matieres_premieres',
    'biocarburants',
    'periods',
    'countries_of_origin',
    'production_sites',
    'delivery_sites',
    'clients',
  ],
  depots: [],
}

export const emptyOperatorSnapshot = {
  years: [2020, 2019],
  lots: {
    draft: 0,
    in: 0,
    accepted: 0,
  },
  filters: [
    'matieres_premieres',
    'biocarburants',
    'periods',
    'countries_of_origin',
    'production_sites',
    'delivery_sites',
    'vendors',
  ],
  depots: [],
}

export const operatorSnapshot = {
  years: [2020, 2019],
  lots: {
    draft: 30,
    in: 20,
    accepted: 10,
  },
  filters: [
    'matieres_premieres',
    'biocarburants',
    'periods',
    'countries_of_origin',
    'production_sites',
    'delivery_sites',
    'vendors',
  ],
  depots: [],
}

export const adminSnapshot = {
  years: [2020, 2019],
  lots: {
    alert: 0,
    correction: 0,
    declaration: 0,
  },
  filters: [
    'matieres_premieres',
    'biocarburants',
    'periods',
    'countries_of_origin',
    'production_sites',
    'delivery_sites',
    'vendors',
    'clients',
  ],
  depots: [],
}

export const emptyLots: Lots = {
  lots: [],
  total: 0,
  total_errors: 0,
  returned: 0,
  from: 0,
  errors: {},
  deadlines: {
    date: "2020-12-31",
    total: 0,
  },
}

export const lots: Lots = {
  lots: [lot],
  total: 1,
  total_errors: 0,
  returned: 1,
  from: 0,
  errors: {},
  deadlines: {
    date: "2020-12-31",
    total: 0,
  },
}

export const manyLots: Lots = {
  lots: [lot, lot, lot, lot, lot, lot, lot, lot, lot, lot],
  total: 200,
  total_errors: 0,
  returned: 10,
  from: 0,
  errors: {},
  deadlines: {
    date: "2020-12-31",
    total: 0,
  },
}

export const baseError = {
  display_to_creator: false,
  display_to_recipient: false,
  display_to_admin: false,
  display_to_auditor: false,

  acked_by_creator: false,
  acked_by_recipient: false,
  acked_by_admin: false,
  acked_by_auditor: false,

  highlighted_by_admin: false,
  highlighted_by_auditor: false,

  is_blocking: false,

  tx: 0,

  field: null,
  fields: null,
  value: "",
  extra: "",
}

const genericErrors: GenericError[] = [
  {
    ...baseError,
    error: "MP_BC_INCOHERENT",
    extra: "Biogaz de blé",
    fields: ["matiere_premiere_code", "biocarburant_code"],
  },
  {
    ...baseError,
    field: "dae",
    error: "MISSING_DAE",
    is_blocking: true,
  },
  {
    ...baseError,
    field: "matiere_premiere_code",
    error: "MISSING_FEEDSTOCK",
    is_blocking: true,
  },
]

export const errorLots: Lots = {
  lots: [lot],
  total: 1,
  total_errors: 1,
  returned: 1,
  from: 0,
  errors: {
    0: genericErrors,
  },
  deadlines: {
    date: "2020-12-31",
    total: 0,
  },
}

export const deadlineLots: Lots = {
  lots: [lot],
  total: 1,
  total_errors: 0,
  returned: 1,
  from: 0,
  errors: {},
  deadlines: {
    date: "2020-02-29",
    total: 1,
  },
}

export const lotDetails: LotDetails = {
  transaction: lot,
  errors: [],
  deadline: "2021-01-31",
  comments: [],
  certificates: {
    production_site_certificate: null,
    supplier_certificate: null,
    vendor_certificate: null,
    double_counting_reference: null,
    unknown_production_site_dbl_counting: null
  },
}

export const errorDetails: LotDetails = {
  transaction: lot,
  errors: genericErrors,
  deadline: "2020-02-29",
  comments: [],
  certificates: {
    production_site_certificate: null,
    supplier_certificate: null,
    vendor_certificate: null,
    double_counting_reference: null,
    unknown_production_site_dbl_counting: null,
  },
}

export const tofixDetails: LotDetails = {
  transaction: {
    ...lot,
    delivery_status: DeliveryStatus.ToFix,
    lot: {
      ...lot.lot,
      status: "Validated",
    },
  },
  errors: [],
  deadline: "2021-01-31",
  comments: [{ entity: operator, comment: "not ok", topic: '' }],
  certificates: {
    production_site_certificate: null,
    supplier_certificate: null,
    vendor_certificate: null,
    double_counting_reference: null,
    unknown_production_site_dbl_counting: null,
  },
}

export const sentDetails: LotDetails = {
  transaction: {
    ...lot,
    delivery_status: DeliveryStatus.Pending,
    lot: {
      ...lot.lot,
      status: "Validated",
    },
  },
  errors: [],
  deadline: "2021-01-31",
  comments: [],
  certificates: {
    production_site_certificate: null,
    supplier_certificate: null,
    vendor_certificate: null,
    double_counting_reference: null,
    unknown_production_site_dbl_counting: null,
  },
}

export const unknownProducerPartial = {
  transaction: {
    lot: {
      producer_is_in_carbure: false,
      carbure_producer: null,
      unknown_producer: "Unknown Producer",
    },
  },
}

export const unknownProdSitePartial = {
  transaction: {
    lot: {
      production_site_is_in_carbure: false,
      carbure_production_site: null,
      unknown_production_site: "Unknown Production Site",
      unknown_production_country: country,
      unknown_production_site_com_date: "2000-01-01",
      unknown_production_site_reference: "2BS - PSITE",
      unknown_production_site_dbl_counting: "ABCDE",
    },
  },
}

export const prodClientPartial = {
  transaction: {
    carbure_client: producer,
  },
}

export const traderClientPartial = {
  transaction: {
    carbure_client: trader,
  },
}

export const unknownClientPartial = {
  transaction: {
    client_is_in_carbure: false,
    carbure_client: null,
    unknown_client: "Unknown Client",
  },
}

export const unknwonDSiteParital = {
  transaction: {
    delivery_site_is_in_carbure: true,
    carbure_delivery_site: null,
    unknown_delivery_site: "Unknown Delivery Site",
    unknown_delivery_site_country: country,
  },
}

export const traderVendorPartial = {
  transaction: {
    carbure_vendor: trader,
  },
}

export const operatorVendorPartial = {
  transaction: {
    carbure_vendor: operator,
  },
}

export const noVendorPartial = {
  transaction: {
    carbure_vendor: null,
  },
}

export const traderAuthorPartial = {
  transaction: {
    lot: {
      added_by: trader,
    },
  },
}

export const operatorAuthorPartial = {
  transaction: {
    lot: {
      added_by: operator,
    },
  },
}

export const stockPartial = {
  transaction: {
    lot: {
      parent_lot: lot,
    },
  },
}

export const lotsSummary = {
  in: {
    [trader.name]: {
      [lot.lot.biocarburant.name]: {
        volume: lot.lot.volume,
        avg_ghg_reduction: lot.lot.ghg_reduction,
        lots: 1,
      },
    },
  },
  out: {
    [operator.name]: {
      [lot.lot.biocarburant.name]: {
        volume: lot.lot.volume,
        avg_ghg_reduction: lot.lot.ghg_reduction,
        lots: 1,
      },
    },
  },
  tx_ids: [lot.id],
  total_volume: 1000,
}

export const generalSummary = {
  transactions: {
    [trader.name]: {
      [operator.name]: {
        [lot.lot.biocarburant.name]: {
          volume: lot.lot.volume,
          avg_ghg_reduction: lot.lot.ghg_reduction,
          lots: 1,
        },
      },
    },
  },
  total_volume: 1000,
  tx_ids: [lot.id],
}

export const declaration = {
  id: 435,
  entity: producer,
  declared: false,
  period: "2021-05-01",
  deadline: "2021-06-30",
  checked: false,
  month: 5,
  year: 2021,
  reminder_count: 0,
}

export function getFilter(field: string) {
  switch (field) {
    case 'matieres_premieres':
      return [{ value: "COLZA", label: "Colza" }]
    case 'biocarburants':
      return [{ value: "EMHV", label: "EMHV" }]
    case 'periods':
      return ["2020-01"]
    case 'countries_of_origin':
      return [{ value: "FR", label: "France" }]
    case 'production_sites':
      return ["Test Production Site"]
    case 'delivery_sites':
      return ["Test Delivery Site"]
    case 'clients':
      return ["Opérateur Test"]
    case 'vendors':
      return ["Producteur Test", "Trader Test"]
  }
}