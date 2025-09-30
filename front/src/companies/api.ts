import { api as apiFetch } from "common/services/api-fetch"
import { EntityType } from "common/types"
import { CertificateTypeEnum } from "api-schema"

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
  certificate_type?: CertificateTypeEnum
) {
  return apiFetch.POST("/entities/add-company", {
    body: {
      activity_description,
      entity_type,
      legal_name,
      name,
      registered_address,
      registered_city,
      registered_country: registered_country_code,
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
