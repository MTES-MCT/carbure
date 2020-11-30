import Cookies from "js-cookie"
import { stringify } from "querystring"

const API_ROOT = `${window.location.origin}/api/v3`

type Params = { [k: string]: any }
type Options = { [k: string]: any }

export type ApiResponse<T> =
  | { status: "error"; message: string }
  | { status: "forbidden"; message: string }
  | { status: "success"; data: T }

function isEmpty(value: any) {
  return typeof value === "undefined" || value === null
}

// keep only parameters that are defined
function filterParams(params: Params) {
  const okParams: Params = {}

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

// check if the api response is correct and return its data
// if there's a problem, throw an error
async function checkResponse<T>(res: Response): Promise<T> {
  if (res.status === 500) {
    throw new Error("Erreur serveur")
  }

  // default data to true in case the api sends nothing
  const parsed = await res.json()
  parsed.data = parsed.data ?? true

  const json: ApiResponse<T> = parsed

  // if the response contains an error, throw it so we can catch it elsewhere
  if (json.status === "error" || json.status === "forbidden") {
    throw new Error(json.message)
  }
  // otherwise, return only the fetched data
  else {
    return json.data
  }
}

function download(endpoint: string, params: Params) {
  let query = params ? "?" + stringify(filterParams(params)) : ""
  return window.open(API_ROOT + endpoint + query)
}

async function get<T = any>(
  endpoint: string,
  params?: Params,
  options?: Options
): Promise<T> {
  let opts: Options = { credentials: "same-origin", ...options }
  let query = params ? "?" + stringify(filterParams(params)) : ""
  const res = await fetch(API_ROOT + endpoint + query, opts)
  return checkResponse<T>(res)
}

async function post<T = any>(
  endpoint: string,
  body?: Params,
  options?: Options
): Promise<T> {
  const fetchOptions: Params = { ...options, method: "POST" }
  const csrf = Cookies.get("csrftoken")

  if (body) {
    fetchOptions.body = toFormData(body)
    fetchOptions.body.append("csrfmiddlewaretoken", csrf)
  }

  const res = await fetch(API_ROOT + endpoint, fetchOptions)
  return checkResponse<T>(res)
}

const api = { download, get, post }
export default api
