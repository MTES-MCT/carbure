import { Certificate, Country, Entity, EntityType } from "carbure/types"



export interface SearchCompanyResult {
  company_preview: SearchCompanyPreview
  warning?: {
    code: string
    meta: null | any
  }
}
export interface SearchCompanyPreview {
  legal_name: string
  registration_id: string
  registered_address: string
  registered_city: string
  registered_zipcode: string
  registered_country: Country
}


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
}

export interface CompanyRegistrationFormValue extends CompanyFormValue {
  certificate: Certificate | undefined
  entity_type: EntityType | undefined
}