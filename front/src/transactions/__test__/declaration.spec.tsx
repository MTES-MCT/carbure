import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { waitWhileLoading } from "common/__test__/helpers"
import { DeclarationDialog } from "../actions/declaration"

import server from "./api"
import { PortalProvider } from "common-v2/components/portal"

const DeclarationSummary = () => (
  <PortalProvider>
    <TestRoot url="/">
      <Route
        path="/"
        element={<DeclarationDialog year={2021} onClose={() => {}} />}
      />
    </TestRoot>
  </PortalProvider>
)

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("display transaction details", async () => {
  render(<DeclarationSummary />)

  await waitWhileLoading()

  screen.getByText("Déclaration de durabilité 2021")

  screen.getByText(
    (_, node) => node?.textContent === "Entrées ▸ 1 lots ▸ 12 345 litres"
  )

  screen.getByText(
    (_, node) => node?.textContent === "Sorties ▸ 1 lots ▸ 12 345 litres"
  )

  screen.getAllByText(
    (_, node) => node?.textContent === "Encore 1 lot en attente de validation"
  )

  const button = screen.getByText("Valider la déclaration").closest("button")
  expect(button).toBeDisabled()
})
