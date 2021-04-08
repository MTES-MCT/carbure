import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import { producer, productionSite } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
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

  await waitWhileLoading()

  expect(screen.getAllByText("Sites de production")).toHaveLength(2)
  screen.getByText("Ajouter un site de production")
  screen.getByText("Aucun site de production trouvé")
})

test("add a production site in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  const button = screen.getByText("Ajouter un site de production")

  userEvent.click(button)

  screen.getByText("Ajout site de production")
  const submit = screen.getByText("Sauvegarder")

  expect(submit.closest("button")).toBeDisabled()

  userEvent.type(screen.getByLabelText("N° d'identification (SIRET)"), "654321")
  userEvent.type(screen.getByLabelText("Nom du site"), "Other Production Site")
  userEvent.type(screen.getByLabelText("Date de mise en service"), "2010-01-31")

  userEvent.type(screen.getByLabelText("Pays"), "France")
  const country = await screen.findByText("France")
  userEvent.click(country)

  expect(submit).not.toBeDisabled()

  userEvent.click(submit)

  await waitWhileLoading()

  await screen.findByText("654321")
  screen.getByText("Other Production Site")
  screen.getByText("France")
  screen.getByText("31/01/2010")
})

test("update a production site details", async () => {
  setProductionSites([productionSite])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  // locate the psite row once it's loaded
  const ps = screen.getByText("Test Production Site")

  // click it to open the details
  userEvent.click(ps)

  // check that the base values in the form are good
  const input = screen.getByLabelText("Nom du site")
  expect(input).toHaveValue("Test Production Site")

  // clear the psite name and type a new one
  userEvent.clear(input)
  userEvent.type(input, "Other Production Site")

  // save the changes
  userEvent.click(screen.getByText("Sauvegarder"))

  await waitWhileLoading()

  // modal is closed
  expect(screen.queryByLabelText("Nom du site")).not.toBeInTheDocument()

  // wait for the api to load the new data and check that it's actually changed
  const row = await screen.findByText("Other Production Site")

  // reopen the details
  userEvent.click(row)

  // verify that the inputs are fine as well
  expect(screen.getByLabelText("Nom du site")).toHaveValue(
    "Other Production Site"
  )
})

test("remove a production site section in settings", async () => {
  setProductionSites([productionSite])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  const deleteButton = await screen.findByTitle(
    "Supprimer le site de production"
  )

  screen.getByText("123456")
  screen.getByText("Test Production Site")
  screen.getByText("France")
  screen.getByText("31/01/2000")

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  screen.getByText("Suppression site")
  userEvent.click(screen.getByText("OK"))

  await waitWhileLoading()

  await screen.findByText("Aucun site de production trouvé")
})
