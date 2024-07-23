import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import { producer, productionSite } from "carbure/__test__/data"
import { getField, setEntity, waitWhileLoading } from "carbure/__test__/helpers"

import server, { setDeliverySites, setProductionSites } from "./api"
import ProductionSitesSettings from "settings/components/production-site"

const SettingsWithHooks = () => {
	return (
		<TestRoot url="/org/0/settings">
			<Route
				path="/org/0/settings"
				element={<ProductionSitesSettings entity={producer} />}
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
	const user = userEvent.setup()
	render(<SettingsWithHooks />)

	await waitWhileLoading()

	const button = screen.getByText("Ajouter un site de production")
	await user.click(button)

	screen.getByText("Ajout site de production")
	const submit = screen.getByText("Sauvegarder")

	expect(submit.closest("button")).toBeDisabled()

	await user.type(getField("N° d'identification \\(SIRET\\)"), "654321")
	await user.type(getField("Nom du site"), "Other Production Site")
	await user.type(getField("Date de mise en service"), "2010-01-31")

	await user.type(getField("Pays"), "France")
	const country = await screen.findByText("France")
	await user.click(country)

	expect(submit).not.toBeDisabled()

	await user.click(submit)

	await waitWhileLoading()

	await screen.findByText("654321")
	screen.getByText("Other Production Site")
	screen.getByText("France")
	screen.getByText("31/01/2010")
})

test("update a production site details", async () => {
	const user = userEvent.setup()
	setProductionSites([productionSite])

	render(<SettingsWithHooks />)

	await waitWhileLoading()

	// locate the psite row once it's loaded
	const ps = screen.getByText("Test Production Site")

	// click it to open the details
	await user.click(ps)

	// check that the base values in the form are good
	const input = getField("Nom du site")
	expect(input).toHaveValue("Test Production Site")

	// clear the psite name and type a new one
	await user.clear(input)
	await user.type(input, "Other Production Site")

	// save the changes
	const save = screen.getByText("Sauvegarder")
	await user.click(save)

	await waitWhileLoading()

	expect(save.closest("button")).not.toBeDisabled()

	await user.click(screen.getByText("Retour"))

	// wait for the api to load the new data and check that it's actually changed
	const row = await screen.findByText("Other Production Site")

	// reopen the details
	await user.click(row)

	// verify that the inputs are fine as well
	expect(getField("Nom du site")).toHaveValue("Other Production Site")

	await user.click(screen.getByText("Retour"))
})

test("remove a production site section in settings", async () => {
	const user = userEvent.setup()
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
	await user.click(deleteButton)
	screen.getByText("Suppression site")
	await user.click(screen.getByText("Supprimer"))

	await waitWhileLoading()

	await screen.findByText("Aucun site de production trouvé")
})
