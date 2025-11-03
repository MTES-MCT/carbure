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
 */
import { createOpenApiHttp } from "openapi-msw"
import { API_PREFIX } from "common/services/api-fetch"
import { newPaths } from "common/services/api-fetch.types"

export const http = createOpenApiHttp<newPaths>({ baseUrl: `/${API_PREFIX}` })
