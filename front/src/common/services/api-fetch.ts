import createClient, { Middleware } from "openapi-fetch"
import { getI18n } from "react-i18next"
import { toFormData } from "./api"
import {
  PathsWithGetMethod,
  QueryParams,
  type newPaths,
} from "./api-fetch.types"

const API_ROOT = `${window.location.origin}/api`

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

export function download<Path extends PathsWithGetMethod>(
  endpoint: Path,
  params: QueryParams<Path>
) {
  return window.open(API_ROOT + endpoint + "?" + toSearchParams(params))
}

export function toSearchParams(params: any) {
  const urlParams = new URLSearchParams()
  for (const key in params) {
    const param = params[key]
    if (Array.isArray(param)) {
      param.forEach((value) => urlParams.append(key, value))
    } else if (!isEmpty(param)) {
      urlParams.append(key, param)
    }
  }
  return urlParams
}

function isEmpty(value: any) {
  const isNull = value === null
  const isUndefined = value === undefined
  const isEmpty = Array.isArray(value) && value.length === 0
  return isNull || isUndefined || isEmpty
}
