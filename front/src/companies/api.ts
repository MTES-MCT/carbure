import { api as apiFetch } from "common/services/api-fetch"
import { EntityType } from "carbure/types"

export function searchCompanyDataBySiren(registration_id: string) {
  console.log("OKOKOK 50")
  return apiFetch.POST("/entities/search-company/", {
    body: { registration_id },
  })
}

export function registerCompany(
  activity_description: string,
  entity_type: EntityType,
  legal_name: string,
  name: string,
  registered_address: string,
  registered_city: string,
  registered_country_code: string,
  registered_zipcode: string,
  registration_id: string,
  sustainability_officer_email: string,
  sustainability_officer_phone_number: string,
  sustainability_officer: string,
  website?: string,
  vat_number?: string,
  certificate_id?: string,
  certificate_type?: string
) {
  console.log("VERYUNSURE 51: not located")
  return apiFetch.POST("/entities/add-company/", {
    body: {
      activity_description,
      entity_type,
      legal_name,
      name,
      registered_address,
      registered_city,
      registered_country_code,
      registered_zipcode,
      registration_id,
      sustainability_officer_email,
      sustainability_officer_phone_number,
      sustainability_officer,
      website,
      vat_number,
      certificate_id,
      certificate_type,
    },
  })
}
