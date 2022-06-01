import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import Account from "../index"
import server, { setAccessRequests } from "./api"
import { producer } from "common-v2/__test__/data"
import { getField, waitWhileLoading } from "common-v2/__test__/helpers"
import { PortalProvider } from "common-v2/components/portal"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

afterEach(() => {
  server.resetHandlers()
  setAccessRequests([])
})

afterAll(() => server.close())

// this component is only here for testing as otherwise we can't use the useGetSettingsHook
// because hooks can only work inside components
const AccountWithHooks = () => {
  return (
    <TestRoot url="/">
      <Route
        path="/"
        element={
          <PortalProvider>
            <Account />
          </PortalProvider>
        }
      />
    </TestRoot>
  )
}

test("empty acces rights in account page", async () => {
  render(<AccountWithHooks />)

  await waitWhileLoading()

  screen.getByText("Demandes d'accès aux sociétés")
  screen.getByText("Aucune autorisation pour ce compte, ajoutez une organisation pour continuer.") // prettier-ignore
})

test("populated acces rights in account page", async () => {
  setAccessRequests([producer])

  render(<AccountWithHooks />)

  // wait for api to load
  await waitWhileLoading()

  screen.getByText("Demandes d'accès aux sociétés")

  // check the first row of request access
  screen.getByText("En attente")
  screen.getByText("Producteur Test")
  screen.getByText("Producteur")
})

test("use the access request menu", async () => {
  render(<AccountWithHooks />)

  await waitWhileLoading()

  const button = screen.getByText("Ajouter une organisation")
  userEvent.click(button)

  const input = getField("Organisation")

  userEvent.type(input, "Test")

  expect(input).toHaveValue("Test")

  // test that the autocomplete is working nicely
  await screen.findByText("Producteur Test")

  // click an the Trader option to select it
  userEvent.click(screen.getByText("Trader Test"))

  // check that the the input has the right selected value
  await screen.findByDisplayValue("Trader Test")

  // validate the choice by clicking the submit button
  userEvent.click(screen.getByText("Demander l'accès"))

  await waitWhileLoading()

  // check that the new access request is listed in the table
  await screen.findByText("En attente")
  screen.getByText("Trader Test")
  screen.getByText("Trader")
})
