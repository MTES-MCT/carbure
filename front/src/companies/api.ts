import api, { Api } from "common/services/api"
import { SearchCompanyResult } from "./types"
import { Certificate, EntityType } from "carbure/types"


export function searchCompanyDataBySiren(
  registration_id: string
) {
  return api.post<Api<SearchCompanyResult>>("/entity/search-company", {
    registration_id
  })
}



export function applyForNewCompany(
  activity_description: string,
  certificate: Certificate,
  entity_type: EntityType,
  legal_name: string,
  registered_address: string,
  registered_city: string,
  registered_country: string,
  registered_zipcode: string,
  registration_id: string,
  sustainability_officer_email: string,
  sustainability_officer_phone_number: string,
  sustainability_officer: string


) {
  console.log('ENVOIE')
  return api.post("/entity/new-company-application", {
    activity_description,
    certificate,
    entity_type,
    legal_name,
    registered_address,
    registered_city,
    registered_country,
    registered_zipcode,
    registration_id,
    sustainability_officer,
    sustainability_officer_email,
    sustainability_officer_phone_number,
  })
}

