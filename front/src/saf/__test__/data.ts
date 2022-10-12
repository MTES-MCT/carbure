import { Biofuel, Country, Feedstock } from "carbure/types";
import { SafTicketSource, SafTicketSourceStatus, SafOperatorSnapshot, SafTicketSourcesResponse } from "saf/types";


export const safOperatorSnapshot: SafOperatorSnapshot = {
  ticket_sources_volume: 15000,
  ticket_sources_available: 2,
  ticket_sources_history: 3,
  tickets: 1,
  tickets_pending: 2,
  tickets_rejected: 1,
  tickets_accepted: 1,
}

export const safClientFilterOptions: string[] = [
  "Air France",
  "CORSAIR",
]

const feedstock1: Feedstock = {
  code: 'LIES_DE_VIN',
  name: 'Lies de vin',
  is_double_compte: false,
  category: 'ANN-IX-A'
}
const bioduel1: Biofuel = {
  code: 'HOC',
  name: 'Autres Huiles Hydrotraitées - Kérosène',
}
const country1: Country = {
  code_pays: 'FR',
  name: 'France',
  name_en: 'France',
  is_in_europe: true
}


export const safTicketSource: SafTicketSource = {
  id: 12343,
  carbure_id: "A12332",
  year: 2021,
  period: 202001,
  date: '20200109',
  total_volume: 10000,
  assigned_volume: 0,
  feedstock: feedstock1,
  biofuel: bioduel1,
  country_of_origin: country1,
  ghg_reduction: 54,
}

export const safTicketSourcesResponse: SafTicketSourcesResponse = {
  saf_ticket_sources: [safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource, safTicketSource],
  from: 1,
  returned: 1,
  total: 11,
  ids: [12343, 12343]
}
