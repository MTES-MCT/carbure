import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import { producer, productionSite } from "carbure/__test__/data"
import { getField, waitWhileLoading } from "carbure/__test__/helpers"

import server, { setDeliverySites, setEntity, setProductionSites } from "./api"
import { PortalProvider } from "common/components/portal"
import ProductionSitesSettings from "settings/components/production-site"

const SettingsWithHooks = () => {
  return (
    <TestRoot url="/org/0/settings">
      <Route
        path="/org/0/settings"
        element={
          <PortalProvider>
            <ProductionSitesSettings entity={producer} />
          </PortalProvider>
        }
      />
    </TestRoot>
  )
}
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

beforeEach(() => setEntity(producer))

afterEach(() => {
  server.resetHandlers()
  setDeliverySites([])
  setProductionSites([])
})

afterAll(() => server.close())

test("check the production site section of the settings", async () => {
  render(<SettingsWithHooks />)

  await waitWhileLoading()

  screen.getByText("Sites de production")
  screen.getByText("Ajouter un site de production")
  screen.getByText("Aucun site de production trouvé")
})

test("add a production site in settings", async () => {
  render(<SettingsWithHooks />)

  await waitWhileLoading()

  const button = screen.getByText("Ajouter un site de production")
  userEvent.click(button)

  screen.getByText("Ajout site de production")
  const submit = screen.getByText("Sauvegarder")

  expect(submit.closest("button")).toBeDisabled()

  userEvent.type(getField("N° d'identification \\(SIRET\\)"), "654321")
  userEvent.type(getField("Nom du site"), "Other Production Site")
  userEvent.type(getField("Date de mise en service"), "2010-01-31")

  userEvent.type(getField("Pays"), "France")
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

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  // locate the psite row once it's loaded
  const ps = screen.getByText("Test Production Site")

  // click it to open the details
  userEvent.click(ps)

  // check that the base values in the form are good
  const input = getField("Nom du site")
  expect(input).toHaveValue("Test Production Site")

  // clear the psite name and type a new one
  userEvent.clear(input)
  userEvent.type(input, "Other Production Site")

  // save the changes
  const save = screen.getByText("Sauvegarder")
  userEvent.click(save)

  expect(save.closest("button")).toBeDisabled()

  await waitWhileLoading()

  expect(save.closest("button")).not.toBeDisabled()

  userEvent.click(screen.getByText("Retour"))

  // wait for the api to load the new data and check that it's actually changed
  const row = await screen.findByText("Other Production Site")

  // reopen the details
  userEvent.click(row)

  // verify that the inputs are fine as well
  expect(getField("Nom du site")).toHaveValue("Other Production Site")

  await waitWhileLoading()

  userEvent.click(screen.getByText("Retour"))
})

test("remove a production site section in settings", async () => {
  setProductionSites([productionSite])

  render(<SettingsWithHooks />)

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
  userEvent.click(screen.getByText("Supprimer"))

  await waitWhileLoading()

  await screen.findByText("Aucun site de production trouvé")
})
