import { mockPostWithResponseData } from "carbure/__test__/helpers"
import { companyResult } from "./data"
import { setupServer } from "msw/node"

export const searchCompanyDataBySirenOk = mockPostWithResponseData(
  "/entity/search-company",
  companyResult
)

export default setupServer(searchCompanyDataBySirenOk)
