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
    if (params[key] !== null && params[key] !== undefined) {
      okParams[key] = params[key]
    }
  }
  return okParams
}

export default api
