import createClient, { Middleware } from "openapi-fetch"
import type { paths } from "api-schema" // generated by openapi-typescript
import { getI18n } from "react-i18next"
import { toFormData } from "./api"

const middleware: Middleware = {
  async onRequest({ request }) {
    request.headers.set("Accept-Language", getI18n().language)
    request.headers.set("xsrfCookieName", "csrftoken")
    request.headers.set("xsrfHeaderName", "X-CSRFTOKEN")

    return request
  },
}

// Enlève le préfixe "/api" de chaque chemin pour générer un type
export type newPaths = {
  [K in keyof paths as K extends `/api${infer Rest}` ? Rest : never]: paths[K]
}

export const api = createClient<newPaths>({
  baseUrl: `${window.location.origin}/api`,
  bodySerializer: (data) => toFormData(data),
})

api.use(middleware)
