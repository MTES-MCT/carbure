import { http } from "common/__test__/http"
import { HttpResponse } from "msw"

export const updateContractOk = http.put(
  "/biomethane/contract/",
  async ({ request }) => {
    const body = await request.json()
    console.log(body)
    return HttpResponse.json(body)
  }
)
