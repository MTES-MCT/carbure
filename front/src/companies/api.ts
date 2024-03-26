import api, { Api } from "common/services/api"
import { SearchCompanyPreview, SearchCompanyResult } from "./types"
import { Certificate, EntityType } from "carbure/types"


export function searchCompanyDataBySiren(
  registration_id: string
) {
  return api.post<Api<SearchCompanyResult>>("/entity/registration/search-company", {
    registration_id
  })
}



export function applyForNewCompany(
  activity_description: string,
  certificate_id: string,
  certificate_type: string,
  entity_type: EntityType,
  legal_name: string,
  registered_address: string,
  registered_city: string,
  registered_country_code: string,
  registered_zipcode: string,
  registration_id: string,
  sustainability_officer_email: string,
  sustainability_officer_phone_number: string,
  sustainability_officer: string


) {
  return api.post("/entity/registration/add-company", {
    activity_description,
    certificate_id,
    certificate_type,
    entity_type,
    legal_name,
    registered_address,
    registered_city,
    registered_country_code,
    registered_zipcode,
    registration_id,
    sustainability_officer_email,
    sustainability_officer_phone_number,
    sustainability_officer,
  })
}

