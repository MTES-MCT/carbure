import { screen, waitForElementToBeRemoved } from "@testing-library/react"

export async function waitWhileLoading() {
  const loaders = await screen.findAllByTitle("Chargement...")
  await waitForElementToBeRemoved(loaders)
}
