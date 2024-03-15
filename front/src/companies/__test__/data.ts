import { CompanyResult } from "companies/types"


const companyResult1: CompanyResult = {
  siren: "75346126",
  nom_complet: "Company Test",
  siege: {
    adresse: "1 rue du paradis",
    code_postal: "75001"
  }
}

const companyResult2: CompanyResult = {
  siren: "75343456",
  nom_complet: "Company Test 2",
  siege: {
    adresse: "1 rue du rhin",
    code_postal: "75002"
  }
}

export const searchCompanyResult: CompanyResult[] = [companyResult1, companyResult2]

