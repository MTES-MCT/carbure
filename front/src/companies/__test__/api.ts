import { mockPostWithResponseData } from "common/__test__/helpers"
import { companyResult } from "./data"
import { setupServer } from "msw/node"

export const searchCompanyDataBySirenOk = mockPostWithResponseData(
  "/entities/search-company/",
  companyResult
)

export default setupServer(searchCompanyDataBySirenOk)
