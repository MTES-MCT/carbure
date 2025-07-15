import createClient, { Middleware } from "openapi-fetch"
import { getI18n } from "react-i18next"
import {
  PathsWithGetMethod,
  QueryParams,
  type newPaths,
} from "./api-fetch.types"
import { getCookie } from "common/utils/cookies"
import { toFormData } from "./api"

export class HttpError extends Error {
  public status: number // Propriété pour stocker le statut HTTP
  public data?: any // Propriété pour stocker des données supplémentaires

  constructor(message: string, status: number, data?: any) {
    super(message)
    this.status = status
    this.data = data

    // Maintenir la pile d'appels correcte (important pour le débogage)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, HttpError)
    }

    // Définit le nom de l'erreur
    this.name = "CustomError"
  }
}

const API_ROOT = `${window.location.origin}/api`

const middleware: Middleware = {
  async onRequest({ request }) {
    const csrfToken = getCookie("csrftoken")
    request.headers.set("Accept-Language", getI18n().language)
    request.headers.set("x-csrftoken", csrfToken ?? "")

    return request
  },
  onResponse: async ({ response }) => {
    if (!response.ok) {
      const message = await response.json()

      throw new HttpError(JSON.stringify(message), response.status, message)
    }
    return response
  },
}

export const api = createClient<newPaths>({
  baseUrl: `${window.location.origin}/api`,
  bodySerializer: (data) => toFormData(data),
})
api.use(middleware)

/**
 * Get the download url for a given endpoint and params
 * @param endpoint - The endpoint to download from
 * @param params - The params to pass to the endpoint
 * @returns The download url
 */
export function getDownloadUrl<Path extends PathsWithGetMethod>(
  endpoint: Path,
  params: QueryParams<Path>
) {
  return API_ROOT + endpoint + "?" + toSearchParams(params)
}

/**
 * Download a file from the given endpoint and params
 * @param endpoint - The endpoint to download from
 * @param params - The params to pass to the endpoint
 * @returns The download url
 */
export function download<Path extends PathsWithGetMethod>(
  endpoint: Path,
  params: QueryParams<Path>
) {
  return window.open(getDownloadUrl(endpoint, params))
}

export function toSearchParams(params: any) {
  const urlParams = new URLSearchParams()
  for (const key in params) {
    const param = params[key]
    if (Array.isArray(param)) {
      param.forEach((value) => urlParams.append(key, value))
    } else if (!isEmpty(param)) {
      urlParams.append(key, param)
    }
  }
  return urlParams
}

function isEmpty(value: any) {
  const isNull = value === null
  const isUndefined = value === undefined
  const isEmpty = Array.isArray(value) && value.length === 0
  return isNull || isUndefined || isEmpty
}
