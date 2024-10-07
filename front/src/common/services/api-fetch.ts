import createClient, { Middleware } from "openapi-fetch"
import { getI18n } from "react-i18next"
import { toFormData } from "./api"
import { type newPaths } from "./api-fetch.types"

const middleware: Middleware = {
  async onRequest({ request }) {
    request.headers.set("Accept-Language", getI18n().language)
    request.headers.set("xsrfCookieName", "csrftoken")
    request.headers.set("xsrfHeaderName", "X-CSRFTOKEN")

    return request
  },
}

export const api = createClient<newPaths>({
  baseUrl: `${window.location.origin}/api`,
  bodySerializer: (data) => toFormData(data),
})
api.use(middleware)
