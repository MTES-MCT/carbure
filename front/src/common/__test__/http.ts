/**
 * Typed MSW HTTP helpers for tests.
 *
 * Purpose:
 * - Wraps MSW's `http` handlers to provide end-to-end type safety for test routes.
 * - `path` is constrained to `keyof newPaths`.
 * - The resolver's return type is inferred from `ResponseType<Path, Method>`,
 *   ensuring mocked payloads match the API contract used by `api-fetch`.
 *
 * What you get:
 * - Strongly typed `http.get|post|put|patch|delete|options|head` helpers.
 * - Compile-time checks that the mocked response matches the expected schema.
 *
 * Usage:
 *   http.get("/api/biomethane/annual-declaration/", () => {
 *     return HttpResponse.json(data) // type-checked against ResponseType<..., "get">
 *   })
 *
 * Notes:
 * - If a route is missing from `newPaths`, add it there so types line up.
 * - Use `apiCall(method, path, resolver, options)` only when the method is dynamic;
 *   otherwise prefer the method-specific helpers.
 */

import {
  http as mswHttp,
  PathParams,
  DefaultBodyType,
  HttpResponseResolver,
} from "msw"
import {
  HttpMethod,
  ResponseType,
  newPaths,
} from "common/services/api-fetch.types"
import { API_PREFIX } from "common/services/api-fetch"

export function apiCall<
  Method extends HttpMethod,
  Params extends PathParams<keyof Params> = PathParams,
  RequestBodyType extends DefaultBodyType = DefaultBodyType,
  Path extends keyof newPaths = keyof newPaths,
>(
  method: Method,
  path: Path,
  resolver: HttpResponseResolver<
    Params,
    RequestBodyType,
    ResponseType<Path, "get"> extends DefaultBodyType
      ? ResponseType<Path, "get">
      : DefaultBodyType
  >,
  options?: Parameters<(typeof mswHttp)[Method]>[2]
) {
  return mswHttp[method](`/${API_PREFIX}${path}`, resolver, options)
}
type Tail<T extends any[]> = T extends [any, ...infer R] ? R : never

type Params<Method extends HttpMethod> = Tail<
  Parameters<typeof apiCall<Method>>
>
const get = (...params: Params<"get">) => apiCall("get", ...params)
const post = (...params: Params<"post">) => apiCall("post", ...params)
const put = (...params: Params<"put">) => apiCall("put", ...params)
const patch = (...params: Params<"patch">) => apiCall("patch", ...params)
const httpDelete = (...params: Params<"delete">) => apiCall("delete", ...params)
const options = (...params: Params<"options">) => apiCall("options", ...params)
const head = (...params: Params<"head">) => apiCall("head", ...params)

export const http = {
  get,
  post,
  put,
  patch,
  delete: httpDelete,
  options,
  head,
}
