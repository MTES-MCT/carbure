import { screen, waitForElementToBeRemoved } from "@testing-library/react"

export function clone(data: any) {
  return JSON.parse(JSON.stringify(data))
}

export async function waitWhileLoading() {
  const loaders = await screen.findAllByTitle("Chargement...")
  await waitForElementToBeRemoved(loaders)
}
