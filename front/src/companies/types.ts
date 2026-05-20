import { Certificate, Country, EntityType } from "common/types"
import { apiTypes } from "common/services/api-fetch.types"

export type SearchCompanyPreview = apiTypes["CompanyPreview"]
export type SearchCompanyResult = apiTypes["ResponseData"]
export type SearchCompanyMeta = apiTypes["Meta"]

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

type WithRequired<T, K extends keyof T> = T & {
  [P in K]-?: Exclude<T[P], undefined>
}

export interface RegisterCompanyPayload extends WithRequired<
  CompanyRegistrationFormValue,
  | "activity_description"
  | "entity_type"
  | "legal_name"
  | "name"
  | "registered_address"
  | "registered_city"
  | "registered_country"
  | "registered_zipcode"
  | "registration_id"
  | "sustainability_officer_email"
  | "sustainability_officer_phone_number"
  | "sustainability_officer"
> {
  certificate_id?: Certificate["certificate_id"]
  certificate_type?: Certificate["certificate_type"]
}
