import { screen, waitForElementToBeRemoved } from "@testing-library/react"

const timing = {
  timeout: 2000,
  interval: 25,
}

export async function waitWhileLoading() {
  const loaders = await screen.findAllByTitle('Chargement...', {}, timing) // prettier-ignore
  await waitForElementToBeRemoved(loaders, timing)
}

export function clone(data: any) {
  return JSON.parse(JSON.stringify(data))
}
