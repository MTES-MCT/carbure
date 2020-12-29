import { lot } from "common/__test__/data"

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

export const snapshot = {
  years: [2020],
  lots: {
    draft: 40,
    validated: 30,
    tofix: 20,
    accepted: 10,
  },
  filters: {
    matieres_premieres: [{ value: "COLZA", label: "Colza" }],
    biocarburants: [{ value: "EMHV", label: "EMHV" }],
    periods: ["2020-12"],
    countries_of_origin: [{ value: "FR", label: "France" }],
    production_sites: ["Test Production Site"],
    delivery_sites: ["Test Delivery Site"],
    clients: ["Opérateur Test"],
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
    date: "2021-12-31",
    total: 0,
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
    periods: ["2020-12"],
    countries_of_origin: [{ value: "FR", label: "France" }],
    production_sites: ["Test Production Site"],
    delivery_sites: ["Test Delivery Site"],
    vendors: ["Producteur Test"],
  },
}

export const operatorLots = {
  lots: [lot],
  total: 1,
  total_errors: 0,
  returned: 1,
  from: 0,
  errors: {},
  deadlines: {
    date: "2021-12-31",
    total: 0,
  },
}
