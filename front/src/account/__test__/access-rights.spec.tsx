import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import Account from "../index"
import { useGetSettings } from "settings/hooks/use-get-settings"
import server, { setAccessRequests } from "./api"
import { producer } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  setAccessRequests([])
})
afterAll(() => server.close())

// this component is only here for testing as otherwise we can't use the useGetSettingsHook
// because hooks can only work inside components
const AccountWithHooks = () => {
  const settings = useGetSettings()
  return <Account settings={settings} />
}

test("empty acces rights in account page", async () => {
  render(<AccountWithHooks />)

  await waitWhileLoading()

  screen.getByText("Demande d'accès")
  screen.getByText("Aucune autorisation pour ce compte, ajoutez une organisation pour continuer.") // prettier-ignore
})

test("populated acces rights in account page", async () => {
  setAccessRequests([producer])

  render(<AccountWithHooks />)

  // wait for api to load
  await waitWhileLoading()

  screen.getByText("Demande d'accès")

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

  const input = await waitFor(() =>
    screen.getByLabelText("Organisation", { selector: "input" })
  )

  userEvent.type(input, "Test")

  expect(input).toHaveValue("Test")

  // test that the autocomplete is working nicely
  await screen.findByText("Producteur Test")
  const trader = screen.getByText("Trader Test")

  // click an the Trader option to select it
  userEvent.click(trader)

  // check that the the input has the right selected value
  expect(input.getAttribute("value")).toBe("Trader Test")

  // validate the choice by clicking the submit button
  userEvent.click(screen.getByText("Demander l'accès"))

  await waitWhileLoading()

  // check that the new access request is listed in the table
  await screen.findByText("En attente")
  screen.getByText("Trader Test")
  screen.getByText("Trader")
})
