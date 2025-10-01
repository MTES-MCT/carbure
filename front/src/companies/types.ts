import { Certificate, Country, EntityType } from "common/types"
import { apiTypes } from "common/services/api-fetch.types"

export type SearchCompanyPreview = apiTypes["CompanyPreview"]
export type SearchCompanyResult = apiTypes["ResponseData"]

export interface CompanyFormValue {
  activity_description: string | undefined
  name: string | undefined
  legal_name: string | undefined
  registered_address: string | undefined
  registered_city: string | undefined
  registered_country: Country | undefined
  registered_zipcode: string | undefined
  registration_id: string | undefined
  sustainability_officer_email: string | undefined
  sustainability_officer_phone_number: string | undefined
  sustainability_officer: string | undefined
  website: string | undefined
  vat_number: string | undefined
}

export interface CompanyRegistrationFormValue extends CompanyFormValue {
  certificate: Certificate | undefined
  entity_type: EntityType | undefined
}
