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

// check if the api response is correct and return its data
// if there's a problem, throw an error
async function checkResponse<T>(res: Response): Promise<T> {
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

  if (body) {
    fetchOptions.body = JSON.stringify(filterParams(body))
  }

  const res = await fetch(url, fetchOptions)
  return checkResponse<T>(res)
}

export default { get, post }
