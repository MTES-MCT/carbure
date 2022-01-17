import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import { deliverySite, producer } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import Settings from "../index"

import server, { setDeliverySites, setEntity } from "./api"

const SettingsWithHooks = () => {
  return (
    <TestRoot url="/org/0/settings">
      {(app) => <Route path="/org/0/settings" element={<Settings />} />}
    </TestRoot>
  )
}

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" })
  setEntity(producer)
})

afterEach(() => {
  server.resetHandlers()
  setDeliverySites([])
})

afterAll(() => server.close())

test("check the delivery site section of the settings", async () => {
  render(<SettingsWithHooks />)

  await waitWhileLoading()

  expect(screen.getAllByText("Dépôts")).toHaveLength(2)
  screen.getByText("Ajouter un dépôt")
  screen.getByText("Aucun dépôt trouvé")
})

test("add a delivery site in settings", async () => {
  render(<SettingsWithHooks />)

  await waitWhileLoading()

  const button = screen.getByText("Ajouter un dépôt")

  userEvent.click(button)

  // wait for dialog to open
  const input = await screen.findByLabelText("Dépôt")
  userEvent.type(input, "Test")

  const option = await screen.findByText("Test Delivery Site")
  userEvent.click(option)

  await waitFor(() => {
    expect(input).toHaveValue("Test Delivery Site")
  })

  userEvent.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("10")
  screen.getByText("Test Delivery Site")
  screen.getByText("Autre")
  screen.getByText("Test City, France")
})

test("check a delivery site details", async () => {
  setDeliverySites([deliverySite])

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  const ds = screen.getByText("Test Delivery Site")
  userEvent.click(ds)

  const input = screen.getByLabelText("Nom du site")

  expect(input).toHaveValue("Test Delivery Site")
})

test("remove a delivery site in settings", async () => {
  setDeliverySites([deliverySite])

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  expect(screen.getAllByText("Dépôts")).toHaveLength(2)

  const deleteButton = screen.getByTitle("Supprimer le dépôt")

  screen.getByText("10")
  screen.getByText("Test Delivery Site")
  screen.getByText("Autre")
  screen.getByText("Test City, France")

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  userEvent.click(screen.getByText("Confirmer"))

  await waitWhileLoading()

  await screen.findByText("Aucun dépôt trouvé")
})
