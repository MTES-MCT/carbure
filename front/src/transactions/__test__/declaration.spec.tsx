import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { getByTextContent, waitWhileLoading } from "common/__test__/helpers"
import { DeclarationDialog } from "../actions/declaration"

import server from "./api"
import { PortalProvider } from "common-v2/components/portal"

const DeclarationSummary = () => (
  <PortalProvider>
    <TestRoot url="/">
      <Route
        path="/"
        element={
          <DeclarationDialog year={2021} years={[2021]} onClose={() => {}} />
        }
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

  screen.getByText("Déclaration de durabilité")

  screen.getByText(/Lots reçus/)
  screen.getByText(/Lots envoyés/)
  screen.getAllByText(/1 lot/)
  screen.getAllByText(/12 345 litres/)

  getByTextContent("Encore 1 lot en attente de validation")

  const button = screen.getByText("Valider la déclaration").closest("button")
  expect(button).toBeDisabled()
})
