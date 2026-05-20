import { api as apiFetch } from "common/services/api-fetch"
import { RegisterCompanyPayload } from "./types"

export function registerCompany(payload: RegisterCompanyPayload) {
  return apiFetch.POST("/entities/add-company", {
    body: {
      activity_description: payload.activity_description,
      entity_type: payload.entity_type,
      legal_name: payload.legal_name,
      name: payload.name,
      registered_address: payload.registered_address,
      registered_city: payload.registered_city,
      registered_country: payload.registered_country.code_pays,
      registered_zipcode: payload.registered_zipcode,
      registration_id: payload.registration_id,
      sustainability_officer_email: payload.sustainability_officer_email,
      sustainability_officer_phone_number:
        payload.sustainability_officer_phone_number,
      sustainability_officer: payload.sustainability_officer,
      website: payload.website,
      vat_number: payload.vat_number,
      certificate_id: payload.certificate_id,
      certificate_type: payload.certificate_type,
    },
  })
}
