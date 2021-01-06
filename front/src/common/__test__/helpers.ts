import { screen, waitForElementToBeRemoved } from "@testing-library/react"

const timeout = 2000
const interval = 25

export async function waitWhileLoading() {
  const loaders = await screen.findAllByTitle("Chargement...", {}, { timeout, interval }) // prettier-ignore
  await waitForElementToBeRemoved(loaders, { timeout, interval })
}

export function clone(data: any) {
  return JSON.parse(JSON.stringify(data))
}
