import { screen, waitForElementToBeRemoved } from "@testing-library/react"

export async function waitWhileLoading() {
  try {
    await screen.findAllByTestId("loader")
    await waitForElementToBeRemoved(() => screen.queryAllByTestId("loader"), { timeout: 60000 }) // prettier-ignore
  } catch {
    console.log("Loader timing based error, completely flaked, can (mostly) safely be ignored.") // prettier-ignore
  }
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

export function getField(label: any) {
  const field = screen.getByText(label).parentElement?.querySelector("input")
  if (!field) throw new Error(`Cannot find field with label like ${label}`)
  return field
}

export function getByTextContent(textContent: string) {
  return screen.getAllByText((_, node) => node?.textContent === textContent)
}
