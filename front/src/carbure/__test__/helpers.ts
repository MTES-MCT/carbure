import { screen, waitForElementToBeRemoved } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

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
  const rx = new RegExp(`^${label}`)
  const field = screen.getByText(rx).parentElement?.querySelector("input")
  if (!field) throw new Error(`Cannot find field with label like ${label}`)
  return field
}

export async function uploadFileField(label: string, file?: any) {
  const user = userEvent.setup()
  if (!file) {
    file = new File(["hello"], "hello.png", { type: "image/png" })
  }
  const dcInput = await getField(label)
  await user.upload(dcInput, file)
  return dcInput
}

export function getByTextContent(textContent: string) {
  return screen.getAllByText((content, node) => {
    return content === textContent || node?.textContent === textContent
  })
}
