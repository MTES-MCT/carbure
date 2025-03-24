import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import { deliverySite, producer } from "common/__test__/data"
import { getField, setEntity, waitWhileLoading } from "common/__test__/helpers"

import { setDeliverySites } from "./api"
import server from "./server"
import { getDeliverySites } from "settings/api/delivery-sites"
import DeliverySitesSettings from "settings/components/delivery-site/delivery-site"

const SettingsWithHooks = () => {
  return (
    <TestRoot url="/org/0/settings">
      <Route
        path="/org/0/settings"
        element={
          <DeliverySitesSettings
            entity={producer}
            getDepots={getDeliverySites}
          />
        }
      />
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

  screen.getByText("Dépôts")
  screen.getByText("Ajouter un dépôt")
  screen.getByText("Aucun dépôt trouvé")
})

test("add a delivery site in settings", async () => {
  const user = userEvent.setup()
  render(<SettingsWithHooks />)

  await waitWhileLoading()

  const button = screen.getByText("Ajouter un dépôt")

  await user.click(button)

  // wait for dialog to open
  const input = getField("Dépôt à ajouter")
  await user.type(input, "Test")

  const option = await screen.findByText("Test Delivery Site")
  await user.click(option)

  await waitFor(() => {
    expect(input).toHaveValue("Test Delivery Site")
  })

  await user.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("10")
  screen.getByText("Test Delivery Site")
  screen.getByText("Autre")
  screen.getByText("Test City, France")
})

test("check a delivery site details", async () => {
  const user = userEvent.setup()
  setDeliverySites([deliverySite])

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  const ds = screen.getByText("Test Delivery Site")
  await user.click(ds)

  const input = getField("Nom du site")

  expect(input).toHaveValue("Test Delivery Site")
})

test("remove a delivery site in settings", async () => {
  const user = userEvent.setup()

  setDeliverySites([deliverySite])

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  screen.getByText("Dépôts")

  const deleteButton = screen.getByTitle("Supprimer le dépôt")

  screen.getByText("10")
  screen.getByText("Test Delivery Site")
  screen.getByText("Autre")
  screen.getByText("Test City, France")

  // click on the delete button and then confirm the action on the popup
  await user.click(deleteButton)
  await user.click(screen.getByText("Supprimer"))

  await waitWhileLoading()

  await screen.findByText("Aucun dépôt trouvé")
})
