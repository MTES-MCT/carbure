import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import { producer } from "common/__test__/data"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"

import server from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check the delivery site section of the settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  screen.getByText("Dépôts")
  screen.getByText("Aucun dépôt trouvé")

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
    screen.getByText("Test Delivery Site")
  })
})
