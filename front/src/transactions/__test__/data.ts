import { lot, operator } from "common/__test__/data"

export const emptySnapshot = {
  years: [2020],
  lots: {
    draft: 0,
    validated: 0,
    tofix: 0,
    accepted: 0,
  },
  filters: {
    matieres_premieres: [],
    biocarburants: [],
    periods: [],
    production_sites: [],
    countries_of_origin: [],
    delivery_sites: [],
    clients: [],
  },
}

export const snapshot = {
  years: [2020, 2019],
  lots: {
    draft: 40,
    validated: 30,
    tofix: 20,
    accepted: 10,
  },
  filters: {
    matieres_premieres: [{ value: "COLZA", label: "Colza" }],
    biocarburants: [{ value: "EMHV", label: "EMHV" }],
    periods: ["2020-01"],
    countries_of_origin: [{ value: "FR", label: "France" }],
    production_sites: ["Test Production Site"],
    delivery_sites: ["Test Delivery Site"],
    clients: ["Opérateur Test"],
  },
}

export const operatorSnapshot = {
  years: [2020],
  lots: {
    draft: 30,
    in: 20,
    accepted: 10,
  },
  filters: {
    matieres_premieres: [{ value: "COLZA", label: "Colza" }],
    biocarburants: [{ value: "EMHV", label: "EMHV" }],
    periods: ["2020-01"],
    countries_of_origin: [{ value: "FR", label: "France" }],
    production_sites: ["Test Production Site"],
    delivery_sites: ["Test Delivery Site"],
    vendors: ["Producteur Test"],
  },
}

export const adminSnapshot = {
  years: [2020],
  lots: {
    alert: 0,
    correction: 0,
    declaration: 0,
  },
  filters: {
    matieres_premieres: [{ value: "COLZA", label: "Colza" }],
    biocarburants: [{ value: "EMHV", label: "EMHV" }],
    periods: ["2020-01"],
    countries_of_origin: [{ value: "FR", label: "France" }],
    production_sites: ["Test Production Site"],
    delivery_sites: ["Test Delivery Site"],
    vendors: ["Producteur Test", "Trader Test"],
    clients: ["Opérateur Test"],
  },
}

export const emptyLots = {
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

export const lots = {
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

export const manyLots = {
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

export const errorLots = {
  lots: [lot],
  total: 1,
  total_errors: 1,
  returned: 1,
  from: 0,
  errors: {
    0: {
      validation_errors: [
        {
          lot_id: 0,
          error: "Matière Première incohérente avec le Biocarburant",
          details: "Biogaz de Blé",
          is_blocking: true,
          is_warning: true,
        },
      ],
      tx_errors: [
        {
          tx_id: 0,
          field: "dae",
          value: "",
          error: "DAE manquant",
        },
      ],
      lots_errors: [
        {
          lot_id: 0,
          field: "matiere_premiere_code",
          value: null,
          error: "Merci de préciser la matière première",
        },
      ],
    },
  },
  deadlines: {
    date: "2020-12-31",
    total: 0,
  },
}

export const deadlineLots = {
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

export const lotDetails = {
  transaction: lot,
  errors: {},
  deadline: "2021-01-31",
  comments: [],
}

export const errorDetails = {
  transaction: lot,
  errors: {
    validation_errors: [
      {
        lot_id: 0,
        error: "Matière Première incohérente avec le Biocarburant",
        details: "Biogaz de Blé",
        is_blocking: true,
        is_warning: true,
      },
      {
        lot_id: 0,
        error: "Volume inhabituellement faible.",
        is_blocking: false,
        is_warning: true,
      },
    ],
    tx_errors: [
      {
        tx_id: 0,
        field: "dae",
        value: "",
        error: "DAE manquant",
      },
    ],
    lots_errors: [
      {
        lot_id: 0,
        field: "matiere_premiere_code",
        value: null,
        error: "Merci de préciser la matière première",
      },
    ],
  },
  deadline: "2020-02-29",
  comments: [],
}

export const tofixDetails = {
  transaction: {
    ...lot,
    delivery_status: "AC",
    lot: {
      ...lot.lot,
      status: "Validated",
    },
  },
  errors: {},
  deadline: "2021-01-31",
  comments: [{ entity: operator, comment: "not ok" }],
}
