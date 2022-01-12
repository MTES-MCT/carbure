import { screen, waitForElementToBeRemoved } from "@testing-library/react"

export async function waitWhileLoading() {
  await screen.findAllByTestId("loader")
  return waitForElementToBeRemoved(() => screen.queryAllByTestId("loader"), {
    timeout: 60000,
  })
}

export function clone(data: any) {
  return JSON.parse(JSON.stringify(data))
}

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
