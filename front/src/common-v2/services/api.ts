import axios from "axios"
import { stringify } from "querystring"

const API_ROOT = `${window.location.origin}/api`

export interface Api<T> {
  status: "success" | "error"
  data?: T
  error?: string
}

export const api = axios.create({
  baseURL: API_ROOT,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFTOKEN",
  paramsSerializer: (params) => stringify(filterParams(params)),
  transformRequest: (data) => toFormData(data),
})

export function download(endpoint: string, params: any) {
  const query = params ? "?" + stringify(filterParams(params)) : ""
  return window.open(API_ROOT + endpoint + query)
}

// keep only parameters that are defined
export function filterParams(params: any) {
  const okParams: any = {}
  for (const key in params) {
    if (!isEmpty(params[key])) {
      okParams[key] = params[key]
    }
  }
  return okParams
}

// converts an javascript object into FormData
function toFormData(obj: any): FormData {
  const formData = new FormData()

  for (const key in obj) {
    if (Array.isArray(obj[key])) {
      obj[key].forEach((value: any) => formData.append(key, value.toString()))
    } else if (!isEmpty(obj[key])) {
      formData.append(key, obj[key])
    }
  }

  return formData
}

function isEmpty(value: any) {
  const isNull = value === null
  const isUndefined = value === undefined
  const isEmpty = Array.isArray(value) && value.length === 0
  return isNull || isUndefined || isEmpty
}

export default api
