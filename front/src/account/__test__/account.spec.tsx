import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import Account from "../index"
import { useGetSettings } from "settings/hooks/use-get-settings"
import server from "./api"

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// this component is only here for testing as otherwise we can't use the useGetSettingsHook
// because hooks can only work inside components
const AccountWithHooks = () => {
  const settings = useGetSettings()
  return <Account settings={settings} />
}

test("load the account page", async () => {
  render(<AccountWithHooks />)

  screen.getByText("Demande d'accès")
  screen.getByText("Identifiants")

  // wait for fake api to load
  await waitFor(() => {
    // check the first row of request access
    screen.getByText("Accepté")
    screen.getByText("Producteur Test")
    screen.getByText("Producteur")

    // check the displayed email
    screen.getByDisplayValue("producer@test.com")
  })
})

test("use the access request menu", async () => {
  render(<AccountWithHooks />)

  const button = screen.getByText("Ajouter une organisation")
  userEvent.click(button)

  const input = await waitFor(() =>
    screen.getByLabelText("Organisation", { selector: "input" })
  )

  userEvent.type(input, "Test")

  // test that the autocomplete is working nicely
  const traderOption = await waitFor(() => {
    expect(input.getAttribute("value")).toBe("Test")
    screen.getByText("Producteur Test", { selector: "li > *" })
    return screen.getByText("Trader Test")
  })

  // click an the Trader option to select it
  userEvent.click(traderOption)

  await waitFor(() => {
    // verify that the input has the selected value
    expect(input.getAttribute("value")).toBe("Trader Test")
  })

  // validate the choice by clicking the submit button
  userEvent.click(screen.getByText("Demander l'accès"))

  // check that the new access request is listed in the table
  await waitFor(() => {
    screen.getByText("En attente")
    screen.getByText("Trader Test")
    screen.getByText("Trader")
  })
})
