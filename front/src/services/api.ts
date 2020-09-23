import { stringify } from "querystring"

const API_ROOT = `${window.location.origin}/api/v3`

type Params = { [k: string]: any }
type Options = { [k: string]: any }

export type ApiResponse<T> =
  | Promise<{ status: "error"; message: string }>
  | Promise<{ status: "forbidden"; message: string }>
  | Promise<{ status: "success"; data: T }>

function readyParams(params: Params) {
  const okParams: Params = {}

  for (const key in params) {
    if (params[key] || params[key] === 0) {
      okParams[key] = params[key]
    }
  }

  return okParams
}

function get<T>(
  endpoint: string,
  params?: Params,
  options?: Options
): ApiResponse<T> {
  let url = API_ROOT + endpoint

  if (params) {
    url += "?" + stringify(readyParams(params))
  }

  return fetch(url, options).then((res) => res.json())
}

function post<T>(
  endpoint: string,
  body?: Params,
  options?: Options
): ApiResponse<T> {
  const fetchOptions: Params = { ...options, method: "POST" }

  if (body) {
    fetchOptions.body = JSON.stringify(readyParams(body))
  }

  return fetch(API_ROOT + endpoint, fetchOptions).then((res) => res.json())
}

export default { get, post }
