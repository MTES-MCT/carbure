import { http, HttpResponse, JsonBodyType } from "msw"
import { generateUser } from "./data"

export const Data = {
  get(key: string) {
    const data = sessionStorage.getItem(key)
    if (data === null) throw new Error(`key "${key}" has no data`)
    return JSON.parse(data)
  },

  set(key: string, value: any) {
    let data
    if (typeof value === "function") {
      data = Data.get(key)
      data = value(data) ?? data
    } else {
      data = value
    }
    const json = JSON.stringify(data)
    sessionStorage.setItem(key, json)
  },
}

export function setEntity(nextEntity: any) {
  Data.set("entity", nextEntity)
}

export const mockGetWithResponseData = <T extends JsonBodyType>(
  url: string,
  data: T
) => {
  return http.get("/api" + url, () => {
    return HttpResponse.json(data)
  })
}

export const mockPostWithResponseData = (
  url: string,
  data?: any,
  withError = false,
  error?: string
) => {
  return http.post("/api" + url, () => {
    return HttpResponse.json(
      {
        status: withError ? "error" : "success",
        error,
        data,
      },
      {
        status: withError ? 400 : 200,
      }
    )
  })
}

export const mockUser = (...params: Parameters<typeof generateUser>) =>
  mockGetWithResponseData("/user", generateUser(...params))
