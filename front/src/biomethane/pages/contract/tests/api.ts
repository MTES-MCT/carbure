import { http } from "common/__test__/http"
import { HttpResponse } from "msw"
import { contractData } from "./contract.data"
import { mockFormDataToObject } from "common/__test__/helpers"

export const updateContractOk = http.put(
  "/biomethane/contract/",
  async ({ request }) => {
    const body = await request.formData()

    return HttpResponse.json({
      ...contractData,
      ...mockFormDataToObject(body),
    })
  }
)
