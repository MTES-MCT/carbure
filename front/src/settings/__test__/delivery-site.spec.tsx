import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import { deliverySite, producer } from "common/__test__/data"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"

import server, { setDeliverySites } from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  setDeliverySites([])
})

afterAll(() => server.close())

test("check the delivery site section of the settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  screen.getByText("Dépôts")
  screen.getByText("Ajouter un dépôt")
  screen.getByText("Aucun dépôt trouvé")
})

test("add a delivery site in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  const button = screen.getByText("Ajouter un dépôt")

  userEvent.click(button)

  // wait for dialog to open
  const input = await waitFor(() => screen.getByLabelText("Dépôt"))

  userEvent.type(input, "Test")

  const option = await waitFor(() =>
    screen.getByText("Test Delivery Site", { selector: "li > *" })
  )

  userEvent.click(option)

  await waitFor(() => {
    expect(input.getAttribute("value")).toBe("Test Delivery Site")
  })

  userEvent.click(screen.getByText("Ajouter"))

  await waitFor(() => {
    screen.getByText("10")
    screen.getByText("Test Delivery Site")
    screen.getByText("Autre")
    screen.getByText("Test City, France")
  })
})

test("remove a delivery site section in settings", async () => {
  setDeliverySites([deliverySite])

  render(<SettingsWithHooks entity={producer} />)

  screen.getByText("Dépôts")

  const deleteButton = await waitFor(() => {
    screen.getByText("10")
    screen.getByText("Test Delivery Site")
    screen.getByText("Autre")
    screen.getByText("Test City, France")

    return screen.getByTitle("Supprimer le dépôt").closest("svg")!
  })

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  userEvent.click(screen.getByText("OK"))

  await waitFor(() => {
    screen.getByText("Aucun dépôt trouvé")
  })
})
