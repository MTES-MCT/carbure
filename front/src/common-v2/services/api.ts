import axios from "axios"
import { stringify } from "querystring"

export interface Api<T> {
  status: "success" | "error"
  data?: T
  error?: string
}

export const api = axios.create({
  baseURL: `${window.location.origin}/api`,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFTOKEN",
  paramsSerializer: (params) => stringify(filterParams(params)),
})

// keep only parameters that are defined
export function filterParams(params: any) {
  const okParams: any = {}
  for (const key in params) {
    const isNull = params[key] === null
    const isUndefined = params[key] === undefined
    const isEmpty = Array.isArray(params[key]) && params[key].length === 0

    if (!isNull && !isUndefined && !isEmpty) {
      okParams[key] = params[key]
    }
  }
  return okParams
}

export default api
