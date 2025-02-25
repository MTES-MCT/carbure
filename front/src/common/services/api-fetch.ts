import createClient, { Middleware } from "openapi-fetch"
import { getI18n } from "react-i18next"
import {
  PathsWithGetMethod,
  QueryParams,
  type newPaths,
} from "./api-fetch.types"
import { getCookie } from "common/utils/cookies"

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

      throw new HttpError(message, response.status, message)
    }
    return response
  },
}

export const api = createClient<newPaths>({
  baseUrl: `${window.location.origin}/api`,
  bodySerializer: (data) => toFormData(data),
})
api.use(middleware)

export function download<Path extends PathsWithGetMethod>(
  endpoint: Path,
  params: QueryParams<Path>
) {
  return window.open(API_ROOT + endpoint + "?" + toSearchParams(params))
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

export function toFileArray(files: FileList) {
  return Array.from(files).map((file) => file)
}

function isEmpty(value: any) {
  const isNull = value === null
  const isUndefined = value === undefined
  const isEmpty = Array.isArray(value) && value.length === 0
  return isNull || isUndefined || isEmpty
}

export function toFormData(obj: any): FormData {
  const formData = new FormData()
  for (const key in obj) {
    if (obj[key] instanceof FileList) {
      Array.from(obj[key]).forEach((value: any) => formData.append(key, value))
    } else if (Array.isArray(obj[key])) {
      obj[key].forEach((value: any) => formData.append(key, value.toString()))
    } else if (!isEmpty(obj[key])) {
      formData.append(key, obj[key])
    }
  }
  return formData
}
// function toFormData(
//   data: any,
//   parentKey: string = "",
//   formData: FormData = new FormData()
// ): FormData {
//   if (data === null || data === undefined) {
//     return formData
//   }

//   if (typeof data === "object" && !(data instanceof File)) {
//     if (Array.isArray(data)) {
//       // Pour les tableaux, ajoute des indices dans la clé (ex: "items[0]")
//       data.forEach((value, index) => {
//         toFormData(value, `${parentKey}[${index}]`, formData)
//       })
//     } else {
//       // Pour les objets, ajoute les clés récursivement
//       Object.keys(data).forEach((key) => {
//         const value = data[key]
//         const newKey = parentKey ? `${parentKey}.${key}` : key
//         toFormData(value, newKey, formData)
//       })
//     }
//   } else {
//     // Ajoute les valeurs simples (string, number, File, etc.)
//     formData.append(parentKey, data)
//   }

//   return formData
// }
