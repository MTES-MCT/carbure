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
