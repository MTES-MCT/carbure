import { stringify } from "querystring"

const API_ROOT = `${window.location.origin}/api/v3`

type Params = { [k: string]: any }
type Options = { [k: string]: any }

export type ApiResponse<T> =
  | Promise<{ status: "error"; message: string }>
  | Promise<{ status: "forbidden"; message: string }>
  | Promise<{ status: "success"; data: T }>

function get<T>(
  endpoint: string,
  params?: Params,
  options?: Options
): ApiResponse<T> {
  return fetch(
    API_ROOT + endpoint + "?" + stringify(params),
    options
  ).then((res) => res.json())
}

function post<T>(
  endpoint: string,
  body?: Params,
  options?: Options
): ApiResponse<T> {
  return fetch(API_ROOT + endpoint, {
    ...options,
    method: "POST",
    body: JSON.stringify(body),
  }).then((res) => res.json())
}

export default { get, post }
