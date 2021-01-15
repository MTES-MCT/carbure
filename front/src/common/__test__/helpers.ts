import { screen, waitForElementToBeRemoved } from "@testing-library/react"

export async function waitWhileLoading(title = "Chargement...") {
  await screen.findAllByTitle(title, {})
  return waitForElementToBeRemoved(() => screen.getAllByTitle(title))
}

export function clone(data: any) {
  return JSON.parse(JSON.stringify(data))
}
