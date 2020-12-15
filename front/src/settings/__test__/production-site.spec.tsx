import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import { producer, productionSite } from "common/__test__/data"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"

import server, { setDeliverySites, setProductionSites } from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  setDeliverySites([])
  setProductionSites([])
})

afterAll(() => server.close())

test("check the production site section of the settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  screen.getByText("Sites de production")
  screen.getByText("Ajouter un site de production")
  screen.getByText("Aucun site de production trouvé")
})

test("add a production site in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  const button = screen.getByText("Ajouter un site de production")

  userEvent.click(button)

  screen.getByText("Ajout site de production")
  const submit = screen.getByText("Sauvegarder")

  expect(submit.hasAttribute("disabled")).toBe(true)

  userEvent.type(screen.getByLabelText("N° d'identification (SIRET)"), "654321")
  userEvent.type(screen.getByLabelText("Nom du site"), "Other Production Site")
  userEvent.type(screen.getByLabelText("Date de mise en service"), "2010-01-31")

  userEvent.type(screen.getByLabelText("Pays"), "France")
  await waitFor(() => userEvent.click(screen.getByText("France")))

  expect(submit.hasAttribute("disabled")).toBe(false)

  userEvent.click(submit)

  await waitFor(() => {
    screen.getByText("654321")
    screen.getByText("Other Production Site")
    screen.getByText("France")
    screen.getByText("31/01/2010")
  })
})

test("update a production site details", async () => {
  setProductionSites([productionSite])

  render(<SettingsWithHooks entity={producer} />)

  // locate the psite row once it's loaded
  const ps = await waitFor(() => screen.getByText("Test Production Site"))

  // click it to open the details
  userEvent.click(ps)

  // check that the base values in the form are good
  const input = screen.getByLabelText("Nom du site")
  expect(input.getAttribute("value")).toBe("Test Production Site")

  // clear the psite name and type a new one
  userEvent.clear(input)
  userEvent.type(input, "Other Production Site")

  // save the changes
  userEvent.click(screen.getByText("Sauvegarder"))

  // wait for the api to load the new data and check that it's actually changed
  const row = await waitFor(() => screen.getByText("Other Production Site"))

  // reopen the details
  userEvent.click(row)

  // verify that the inputs are fine as well
  expect(screen.getByLabelText("Nom du site").getAttribute("value")).toBe(
    "Other Production Site"
  )
})

test("remove a production site section in settings", async () => {
  setProductionSites([productionSite])

  render(<SettingsWithHooks entity={producer} />)

  const deleteButton = await waitFor(() => {
    screen.getByText("123456")
    screen.getByText("Test Production Site")
    screen.getByText("France")
    screen.getByText("31/01/2000")

    return screen.getByTitle("Supprimer le site de production").closest("svg")!
  })

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  screen.getByText("Suppression site")
  userEvent.click(screen.getByText("OK"))

  await waitFor(() => {
    screen.getByText("Aucun site de production trouvé")
  })
})
