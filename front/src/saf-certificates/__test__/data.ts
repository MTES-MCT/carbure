import { Biofuel, Country, Feedstock } from "carbure/types";
import { SafCertificate, SafCertificateStatus, SafSnapshot } from "saf-certificates/types";


export const safSnapshot: SafSnapshot = {
  to_assign: 4,
  to_assign_available: 3,
  to_assign_history: 1,
  pending: 2,
  rejected: 1,
  accepted: 2
}

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

export const safCertificate: SafCertificate = {
  id: 12343,
  carbure_id: "A12332",
  year: 2021,
  period: 202001,
  date: null,
  carbure_client: null,
  status: SafCertificateStatus.Accepted,
  total_volume: 10000,
  assigned_volume: 0,
  assigned_clients: [],
  feedstock: feedstock1,
  biofuel: bioduel1,
  country_of_origin: country1,
  ghg_reduction: 54,
}

export const safCertificates: SafCertificate[] = [safCertificate, safCertificate]
