import { Route } from "react-router-dom"
import { render, TestRoot } from "setupTests"
import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Entity } from "carbure/types"

import { operator, producer } from "carbure/__test__/data"
import LotDetails from "../components/lots/index"
import { LotDetails as LotDetailsData } from "transaction-details/types"

import server from "./api"

import {
	Data,
	getField,
	setEntity,
	waitWhileLoading,
} from "carbure/__test__/helpers"
import { clickOnCheckboxesAndConfirm } from "../../transactions/__test__/helpers"
import {
	lotDetails,
	errorDetails,
	tofixDetails,
	rejectedDetails,
	sentDetails,
} from "./data"
import HashRoute from "common/components/hash-route"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
beforeEach(() => Data.set("lot-details", lotDetails))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const LotDetailsWithRouter = ({ entity }: { entity: Entity }) => {
	setEntity(entity)
	return (
		<TestRoot url={`/org/${entity.id}/transactions/2021/drafts/imported#lot/0`}>
			<Route
				path="/org/:entity/transactions/:year/:status/:category"
				element={
					<HashRoute path="lot/:id" element={<LotDetails neighbors={[]} />} />
				}
			/>
			<Route path="/draft/imported" element={<p>EMPTY</p>} />
		</TestRoot>
	)
}

function checkLotFields() {
	getField("N° document d'accompagnement")
	getField("Quantité")
	getField("Biocarburant")
	getField("Matière première")
	getField("Pays d'origine de la matière première")
}

function checkProductionFields() {
	getField("Site de production")
	getField("Certificat du site de production")
	getField("Pays de production")
	getField("Date de mise en service")
	// getField("Certificat double-comptage")
}

function checkOriginFields() {
	getField("Producteur")
	getField("Fournisseur")
	getField("Certificat du fournisseur")
	getField("Champ libre")
}

function checkDeliveryFields() {
	getField("Client")
	getField("Site de livraison")
	getField("Pays de livraison")
	getField("Date de livraison")
}

function checkGESFields() {
	getField("EEC")
	getField("EL")
	getField("EP")
	getField("ETD")
	getField("EU")

	getField("ESCA")
	getField("ECCS")
	getField("ECCR")
	getField("EEE")

	getField("Total")
	getField("Réd. RED I")
}

test("display transaction details", async () => {
	render(<LotDetailsWithRouter entity={producer} />)

	await screen.findByText(/Lot #TEST01/)

	await screen.findByDisplayValue("DAETEST")

	await screen.findByDisplayValue("12345")
	await screen.findByDisplayValue("EMHV")
	await screen.findByDisplayValue("Colza")
	await screen.findByDisplayValue("2020-01-31")
	await screen.findAllByDisplayValue("Producteur Test")
	await screen.findByDisplayValue("Test Production Site")
	await screen.findByDisplayValue("2000-01-31")
	await screen.findByDisplayValue("Opérateur Test")
	await screen.findByDisplayValue("Test Delivery Site")
	await screen.findByDisplayValue("12")
	await screen.findByDisplayValue("1")
	await screen.findByDisplayValue("11 gCO2eq/MJ")
	await screen.findByDisplayValue("86,87%")

	const countries = await screen.findAllByDisplayValue("France")
	const zeros = await screen.findAllByDisplayValue("0")

	expect(countries.length).toBe(3)
	expect(zeros.length).toBe(7)
})

test("edit transaction details", async () => {
	const user = userEvent.setup()

	render(<LotDetailsWithRouter entity={producer} />)

	const save: any = await screen.findByText("Sauvegarder")

	screen.getAllByText(/^Lot/)

	const dae = getField("N° document d'accompagnement")
	await user.clear(dae)
	await user.type(dae, "DAETEST")

	const vol = getField("Quantité")
	await user.clear(vol)
	await user.type(vol, "20000")

	const bio = getField("Biocarburant")
	await user.clear(bio)
	await user.type(bio, "EM")
	await user.click(await screen.findByText("EMHV"))
	await screen.findByDisplayValue("EMHV")

	const mp = getField("Matière première")
	await user.clear(mp)
	await user.type(mp, "Co")
	await user.click(await screen.findByText("Colza"))
	await screen.findByDisplayValue("Colza")

	const ct: any = getField("Pays d'origine de la matière première")
	await user.clear(ct)
	await user.type(ct, "Fra")
	await user.click(await screen.findByText("France"))
	await screen.findAllByDisplayValue("France")

	const dd = getField("Date de livraison")
	await user.clear(dd)
	await user.type(dd, "2021-31-01")

	screen.getAllByDisplayValue("Producteur Test")

	const ps = getField("Site de production")
	await user.clear(ps)
	await user.type(ps, "Test")
	await user.click(await screen.findByText("Test Production Site"))
	await screen.findByDisplayValue("Test Production Site")

	const cli = getField("Client")
	await user.clear(cli)
	await user.type(cli, "Test")
	await user.click(await screen.findByText("Opérateur Test"))
	await screen.findByDisplayValue("Opérateur Test")

	const ds = getField("Site de livraison")
	await user.clear(ds)
	await user.type(ds, "Test")
	await user.click(await screen.findByText("Test Delivery Site"))
	await screen.findByDisplayValue("Test Delivery Site")

	const cl = getField("Champ libre")
	await user.clear(cl)
	await user.type(cl, "blabla")

	const eec = getField("EEC")
	await user.clear(eec)
	await user.type(eec, "10")

	const el = getField("EL")
	await user.clear(el)
	await user.type(el, "1.1")

	const ep = getField("EP")
	await user.clear(ep)
	await user.type(ep, "1.2")

	const etd = getField("ETD")
	await user.clear(etd)
	await user.type(etd, "1.3")

	const eu = getField("EU")
	await user.clear(eu)
	await user.type(eu, "1.4")

	const esca = getField("ESCA")
	await user.clear(esca)
	await user.type(esca, "1.1")

	const eccs = getField("ECCS")
	await user.clear(eccs)
	await user.type(eccs, "1.2")

	const eccr = getField("ECCR")
	await user.clear(eccr)
	await user.type(eccr, "1.3")

	const eee = getField("EEE")
	await user.clear(eee)
	await user.type(eee, "1.4")

	expect(save.closest("button")).not.toBeDisabled()

	await user.click(save)

	await screen.findByDisplayValue("DAETEST UPDATED")
}, 30000)

test("check transaction errors", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", errorDetails)
	render(<LotDetailsWithRouter entity={producer} />)

	await screen.findByText("Brouillon")

	const comdate = screen.getByTitle(
		"La date de mise en service du site de production est manquante"
	)
	expect(comdate.closest("[data-field]")).toHaveAttribute("data-error")

	screen.getByText("Erreurs (2)")

	screen.getByText("Le site de production n'est pas reconnu", {
		selector: "li",
	})
	screen.getByText(
		"La date de mise en service du site de production est manquante",
		{ selector: "li" }
	)

	const warnings = screen.getByText("Remarques (1)")
	await user.click(warnings)

	screen.getByText("Certificat du site de production absent")

	await user.click(screen.getByText("Retour"))
})

test("check transaction comments", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", tofixDetails)
	render(<LotDetailsWithRouter entity={producer} />)

	await screen.findByText("En correction")

	const comments = screen.getByText("Commentaires (1)")
	await user.click(comments)

	screen.getByText(/Opérateur Test:/)
	screen.getByText("Ces lots ont été affectés par erreur")

	await user.type(
		screen.getByPlaceholderText("Entrez un commentaire..."),
		"test ok"
	)

	await user.click(screen.getByText("Envoyer"))

	await screen.findByText("Commentaires (2)")
	screen.getByText(/Producteur Test:/)
	screen.getByText("test ok")

	await user.click(screen.getByText("Retour"))
})

test("send draft lot from details", async () => {
	const user = userEvent.setup()

	render(<LotDetailsWithRouter entity={producer} />)

	// click on the send action
	const send = await screen.findByText("Envoyer")
	await user.click(send)

	// dialog to confirm the sending
	const title = await screen.findByText("Envoyer ce brouillon")
	await clickOnCheckboxesAndConfirm(user)

	await screen.findByText("En attente")
	expect(title).not.toBeInTheDocument()

	await user.click(screen.getByText("Retour"))
})

test("delete draft lot from details", async () => {
	const user = userEvent.setup()

	render(<LotDetailsWithRouter entity={producer} />)

	// click on the send action
	const send = await screen.findByText("Supprimer")
	await user.click(send)

	// dialog to confirm the sending
	const title = screen.getByText("Supprimer ce lot")
	await user.click(screen.getAllByText("Supprimer")[1])

	await waitFor(() => expect(title).not.toBeInTheDocument())
})

test("resend tofix lot from details", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", tofixDetails)
	render(<LotDetailsWithRouter entity={producer} />)

	// click on the send action
	const send = await screen.findByText("Confirmer la correction")
	await user.click(send)

	// confirm the sending
	const title = screen.getByText("Confirmer la correction", { selector: "h1" })
	await user.click(screen.getByText("Confirmer correction"))

	await screen.findByText("Corrigé")
	expect(title).not.toBeInTheDocument()

	const comments = screen.getByText("Commentaires (1)")
	await user.click(comments)

	await user.click(screen.getByText("Retour"))
})

test("delete tofix lot from details", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", rejectedDetails)
	render(<LotDetailsWithRouter entity={producer} />)

	// click on the send action
	const send = await screen.findByText("Supprimer")
	await user.click(send)

	// confirm the sending
	const title = screen.getByText("Supprimer ce lot")
	await user.click(screen.getAllByText("Supprimer")[1])

	await waitFor(() => expect(title).not.toBeInTheDocument())
})

test("accept inbox lot from details", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", sentDetails)
	render(<LotDetailsWithRouter entity={operator} />)

	await screen.findByText("En attente")

	await user.click(await screen.findByText("Accepter"))
	await user.click(await screen.findByText("Incorporation"))

	// confirm the transaction
	screen.getByText("Incorporation de lot", { selector: "h1" })
	await user.click(screen.getByText("Incorporation"))

	await screen.findByText("Incorporé")
})

test("accept sous reserve inbox lot from details", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", sentDetails)

	render(<LotDetailsWithRouter entity={operator} />)

	await screen.findByText("En attente")

	await user.click(await screen.findByText("Demander une correction"))

	screen.getByText("Demander une correction", { selector: "h1" })
	await user.type(getField("Commentaire"), "test is incorrect") // prettier-ignore
	await user.click(screen.getByText("Demander correction"))

	await screen.findByText("En correction")
})

test("reject inbox lot from details", async () => {
	const user = userEvent.setup()

	Data.set("lot-details", sentDetails)

	render(<LotDetailsWithRouter entity={operator} />)

	await waitWhileLoading()

	await screen.findByText("En attente")

	await user.click(await screen.findByText("Refuser"))

	// confirm the transaction
	await screen.findByText("Refuser ce lot", { selector: "h1" })
	const rejectButton = screen.getAllByText("Refuser")[1]
	expect(rejectButton).toBeDisabled()
	const comment = getField("Commentaire")
	await user.type(comment, "not for me") // prettier-ignore
	expect(rejectButton).not.toBeDisabled()
	await user.click(rejectButton)

	await waitWhileLoading()

	await screen.findByText("Refusé")
})

test("transaction details form as producer - producer trades unknown producer lot to operator", async () => {
	Data.set("lot-details", sentDetails)
	Data.set("lot-details", (details: LotDetailsData) => {
		details.lot.carbure_producer = null
		details.lot.unknown_producer = "Unknown Producer"
		details.lot.carbure_supplier = null
		details.lot.unknown_supplier = "Unknown Supplier"
		details.lot.vendor_certificate = "ISCC1000 - Vendor"
		details.lot.carbure_production_site = null
		details.lot.unknown_production_site = "Unknown Production Site"
	})

	render(<LotDetailsWithRouter entity={producer} />)

	await screen.findByDisplayValue("DAETEST")

	checkLotFields()
	checkOriginFields()
	checkProductionFields()
	checkDeliveryFields()
	await checkGESFields()

	await screen.findByDisplayValue("Unknown Producer")

	const supplier = getField("Fournisseur")
	expect(supplier).toHaveValue("Unknown Supplier")

	const supplierCertif = getField("Certificat du fournisseur")
	expect(supplierCertif).toHaveValue("ISCC2000 - Supplier")

	expect(getField("Site de production")).toHaveValue("Unknown Production Site")

	const certif = getField("Certificat du site de production")
	expect(certif).toHaveValue("2BS - KNOWN PSITE")

	const psiteCountry = getField("Pays de production")
	expect(psiteCountry).toHaveValue("France")

	expect(getField("Votre certificat")).toHaveValue("ISCC1000 - Vendor")
})

test("transaction details form as operator - producer trades unknown producer lot to operator", async () => {
	Data.set("lot-details", sentDetails)
	Data.set("lot-details", (details: LotDetailsData) => {
		details.lot.carbure_producer = null
		details.lot.unknown_producer = "Unknown Producer"
		details.lot.supplier_certificate = "ISCC1000 - Vendor"
		details.lot.carbure_production_site = null
		details.lot.unknown_production_site = "Unknown Production Site"
	})

	render(<LotDetailsWithRouter entity={operator} />)

	await screen.findByDisplayValue("DAETEST")

	checkLotFields()
	checkOriginFields()
	checkProductionFields()
	checkDeliveryFields()
	checkGESFields()

	await screen.findByDisplayValue("Unknown Producer")
	await screen.findByDisplayValue("Producteur Test")
	await screen.findByDisplayValue("ISCC1000 - Vendor")
	await screen.findByDisplayValue("Unknown Production Site")
	await screen.findByDisplayValue("2BS - KNOWN PSITE")
	expect(getField("Pays de production")).toHaveValue("France")
})

test("transaction details form as operator - operator self accepts lot", async () => {
	Data.set("lot-details", sentDetails)
	Data.set("lot-details", (details: LotDetailsData) => {
		details.lot.carbure_producer = null
		details.lot.unknown_producer = "Unknown Producer"
		details.lot.carbure_supplier = null
		details.lot.unknown_supplier = "Unknown Supplier"
		details.lot.vendor_certificate = "ISCC1000 - Vendor"
		details.lot.carbure_production_site = null
		details.lot.unknown_production_site = "Unknown Production Site"
	})

	render(<LotDetailsWithRouter entity={operator} />)

	await waitWhileLoading()

	await screen.findByDisplayValue("DAETEST")

	checkLotFields()
	checkOriginFields()
	checkProductionFields()
	checkDeliveryFields()
	checkGESFields()

	await screen.findByDisplayValue("Unknown Producer")
	await screen.findByDisplayValue("Unknown Supplier")
	await screen.findByDisplayValue("ISCC2000 - Supplier")
	await screen.findByDisplayValue("Unknown Production Site")
	await screen.findByDisplayValue("2BS - KNOWN PSITE")
	await screen.findAllByDisplayValue("France")
})
