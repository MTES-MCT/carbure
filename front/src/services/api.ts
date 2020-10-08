import Cookies from "js-cookie"
import { stringify } from "querystring"

const API_ROOT = `${window.location.origin}/api/v3`

type Params = { [k: string]: any }
type Options = { [k: string]: any }

export type ApiResponse<T> =
  | { status: "error"; message: string }
  | { status: "forbidden"; message: string }
  | { status: "success"; data: T }

// keep only parameters that are defined
function filterParams(params: Params) {
  const okParams: Params = {}

  for (const key in params) {
    if (params[key] || params[key] === 0) {
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
    } else if (obj[key] || obj[key] === 0) {
      formData.append(key, obj[key].toString())
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

  const json: ApiResponse<T> = await res.json()

  // if the response contains an error, throw it so we can catch it elsewhere
  if (json.status === "error" || json.status === "forbidden") {
    throw new Error(json.message)
  } else {
    // otherwise, return only the fetched data
    return json.data
  }
}

async function get<T = any>(
  endpoint: string,
  params?: Params,
  options?: Options
): Promise<T> {
  let url = API_ROOT + endpoint

  if (params) {
    url += "?" + stringify(filterParams(params))
  }

  const res = await fetch(url, options)
  return checkResponse<T>(res)
}

async function post<T = any>(
  endpoint: string,
  body?: Params,
  options?: Options
): Promise<T> {
  const url = API_ROOT + endpoint
  const fetchOptions: Params = { ...options, method: "POST" }
  const csrf = Cookies.get("csrftoken")

  if (body) {
    fetchOptions.body = toFormData(body)
    fetchOptions.body.append("csrfmiddlewaretoken", csrf)
  }

  const res = await fetch(url, fetchOptions)
  return checkResponse<T>(res)
}

export default { get, post }
