import { Route, Routes } from "react-router-dom"
import { render, TestRoot } from "setupTests"
import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Entity } from "carbure/types"

import { operator, producer } from "common/__test__/data"
import LotDetails from "../index"
import { LotDetails as LotDetailsData } from "lot-details/types"

import server from "./api"

import { Data, getField } from "common/__test__/helpers"
import { PortalProvider } from "common-v2/components/portal"
import { clickOnCheckboxesAndConfirm } from "../../transactions/__test__/helpers"
import { setEntity } from "settings/__test__/api"
import {
  lotDetails,
  errorDetails,
  tofixDetails,
  rejectedDetails,
  sentDetails,
} from "./data"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
beforeEach(() => Data.set("lot-details", lotDetails))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const LotDetailsWithRouter = ({ entity }: { entity: Entity }) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/transactions/2021/draft/pending/0`}>
      <Route
        path="/org/:entity/transactions/:year/:status/:category/:id"
        element={
          <PortalProvider>
            <LotDetails neighbors={[]} />
          </PortalProvider>
        }
      />
      <Route path="/draft/pending" element={<p>EMPTY</p>} />
    </TestRoot>
  )
}

function checkLotFields() {
  getField("N° document d'accompagnement *")
  getField("Volume en litres (Ethanol à 20°, autres à 15°) *")
  getField("Biocarburant *")
  getField(/^Matière première */)
  getField("Pays d'origine de la matière première *")
}

function checkProductionFields() {
  getField(/^Site de production/)
  getField("Certificat du site de production")
  getField("Pays de production")
  getField("Date de mise en service")
  getField("Certificat double-comptage")
}

function checkOriginFields() {
  getField("Producteur")
  getField("Fournisseur")
  getField("Certificat du fournisseur")
  getField("Champ libre")
}

function checkDeliveryFields() {
  getField(/^Client/)
  getField(/^Site de livraison/)
  getField("Pays de livraison")
  getField("Date de livraison *")
}

function checkGESFields() {
  getField("Émissions")
  getField("EEC")
  getField("EL")
  getField("EP *")
  getField("ETD *")
  getField("EU")

  getField("Réductions")
  getField("ESCA")
  getField("ECCS")
  getField("ECCR")
  getField("EEE")

  getField("Total")
  getField("Réd. RED I")
}

test("display transaction details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  await screen.findByText(/Détails du lot #TEST01/)

  screen.getByDisplayValue("DAETEST")

  screen.getByDisplayValue("12345")
  screen.getByDisplayValue("EMHV")
  screen.getByDisplayValue("Colza")
  screen.getByDisplayValue("2020-01-31")
  screen.getAllByDisplayValue("Producteur Test")
  screen.getByDisplayValue("Test Production Site")
  screen.getByDisplayValue("2000-01-31")
  screen.getByDisplayValue("Opérateur Test")
  screen.getByDisplayValue("Test Delivery Site")
  screen.getByDisplayValue("12")
  screen.getByDisplayValue("1")
  screen.getByDisplayValue("11 gCO2eq/MJ")
  screen.getByDisplayValue("86,87%")

  const countries = screen.getAllByDisplayValue("France")
  const zeros = screen.getAllByDisplayValue("0")

  expect(countries.length).toBe(3)
  expect(zeros.length).toBe(7)
})

test("edit transaction details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  const save: any = await screen.findByText("Sauvegarder")

  screen.getByText(/^Détails du lot/)

  const dae = getField("N° document d'accompagnement *")
  userEvent.clear(dae)
  userEvent.type(dae, "DAETEST")

  const vol = getField("Volume en litres (Ethanol à 20°, autres à 15°) *")
  userEvent.clear(vol)
  userEvent.type(vol, "20000")

  const bio = getField("Biocarburant *")
  userEvent.clear(bio)
  userEvent.type(bio, "EM")
  userEvent.click(await screen.findByText("EMHV"))
  await screen.findByDisplayValue("EMHV")

  const mp = getField(/Matière première \*/)
  userEvent.clear(mp)
  userEvent.type(mp, "Co")
  userEvent.click(await screen.findByText("Colza"))
  await screen.findByDisplayValue("Colza")

  const ct: any = getField("Pays d'origine de la matière première *")
  userEvent.clear(ct)
  userEvent.type(ct, "Fra")
  userEvent.click(await screen.findByText("France"))
  await screen.findAllByDisplayValue("France")

  const dd = getField("Date de livraison *")
  userEvent.clear(dd)
  userEvent.type(dd, "2021-31-01")

  screen.getAllByDisplayValue("Producteur Test")

  const ps = getField(/^Site de production/)
  userEvent.clear(ps)
  userEvent.type(ps, "Test")
  userEvent.click(await screen.findByText("Test Production Site"))
  await screen.findByDisplayValue("Test Production Site")

  const cli = getField(/^Client/)
  userEvent.clear(cli)
  userEvent.type(cli, "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))
  await screen.findByDisplayValue("Opérateur Test")

  const ds = getField(/^Site de livraison/)
  userEvent.clear(ds)
  userEvent.type(ds, "Test")
  userEvent.click(await screen.findByText("Test Delivery Site"))
  await screen.findByDisplayValue("Test Delivery Site")

  const cl = getField("Champ libre")
  userEvent.clear(cl)
  userEvent.type(cl, "blabla")

  const eec = getField("EEC")
  userEvent.clear(eec)
  userEvent.type(eec, "10")

  const el = getField("EL")
  userEvent.clear(el)
  userEvent.type(el, "1.1")

  const ep = getField("EP *")
  userEvent.clear(ep)
  userEvent.type(ep, "1.2")

  const etd = getField("ETD *")
  userEvent.clear(etd)
  userEvent.type(etd, "1.3")

  const eu = getField("EU")
  userEvent.clear(eu)
  userEvent.type(eu, "1.4")

  const esca = getField("ESCA")
  userEvent.clear(esca)
  userEvent.type(esca, "1.1")

  const eccs = getField("ECCS")
  userEvent.clear(eccs)
  userEvent.type(eccs, "1.2")

  const eccr = getField("ECCR")
  userEvent.clear(eccr)
  userEvent.type(eccr, "1.3")

  const eee = getField("EEE")
  userEvent.clear(eee)
  userEvent.type(eee, "1.4")

  expect(save.closest("button")).not.toBeDisabled()

  userEvent.click(save)

  await screen.findByDisplayValue("DAETEST UPDATED")
}, 30000)

test("check transaction errors", async () => {
  Data.set("lot-details", errorDetails)
  render(<LotDetailsWithRouter entity={producer} />)

  await screen.findByText("Brouillon")

  const psite = screen.getByTitle("Le site de production n'est pas reconnu")
  expect(psite.closest("svg")).toBeInTheDocument()
  expect(psite.closest("[data-field]")).toHaveAttribute("data-error")

  const comdate = screen.getByTitle(
    "La date de mise en service du site de production est manquante"
  )
  expect(comdate.closest("[data-field]")).toHaveAttribute("data-error")

  const errors = screen.getByText("Erreurs (2)")
  userEvent.click(errors)

  screen.getByText("Le site de production n'est pas reconnu", {
    selector: "li",
  })
  screen.getByText(
    "La date de mise en service du site de production est manquante",
    { selector: "li" }
  )

  const warnings = screen.getByText("Remarques (1)")
  userEvent.click(warnings)

  screen.getByText("Certificat du site de production absent")

  userEvent.click(screen.getByText("Retour"))
})

test("check transaction comments", async () => {
  Data.set("lot-details", tofixDetails)
  render(<LotDetailsWithRouter entity={producer} />)

  await screen.findByText("En correction")

  const comments = screen.getByText("Commentaires (1)")
  userEvent.click(comments)

  screen.getByText(/Opérateur Test:/)
  screen.getByText("Ces lots ont été affectés par erreur")

  userEvent.type(
    screen.getByPlaceholderText("Entrez un commentaire..."),
    "test ok"
  )

  userEvent.click(screen.getByText("Envoyer"))

  await screen.findByText("Commentaires (2)")
  screen.getByText(/Producteur Test:/)
  screen.getByText("test ok")

  userEvent.click(screen.getByText("Retour"))
})

test("send draft lot from details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  // click on the send action
  const send = await screen.findByText("Envoyer")
  userEvent.click(send)

  // dialog to confirm the sending
  const title = screen.getByText("Envoyer ce brouillon")
  clickOnCheckboxesAndConfirm()

  await screen.findByText("En attente")
  expect(title).not.toBeInTheDocument()

  userEvent.click(screen.getByText("Retour"))
})

test("delete draft lot from details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // dialog to confirm the sending
  const title = screen.getByText("Supprimer ce lot")
  userEvent.click(screen.getAllByText("Supprimer")[1])

  await waitFor(() => expect(title).not.toBeInTheDocument())
})

test("resend tofix lot from details", async () => {
  Data.set("lot-details", tofixDetails)
  render(<LotDetailsWithRouter entity={producer} />)

  // click on the send action
  const send = await screen.findByText("Confirmer la correction")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Confirmer la correction", { selector: "h1" })
  userEvent.click(screen.getByText("Confirmer correction"))

  await screen.findByText("Corrigé")
  expect(title).not.toBeInTheDocument()

  const comments = screen.getByText("Commentaires (1)")
  userEvent.click(comments)

  userEvent.click(screen.getByText("Retour"))
})

test("delete tofix lot from details", async () => {
  Data.set("lot-details", rejectedDetails)
  render(<LotDetailsWithRouter entity={producer} />)

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Supprimer ce lot")
  userEvent.click(screen.getAllByText("Supprimer")[1])

  await waitFor(() => expect(title).not.toBeInTheDocument())
})

test("accept inbox lot from details", async () => {
  Data.set("lot-details", sentDetails)
  render(<LotDetailsWithRouter entity={operator} />)

  await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Accepter"))
  userEvent.click(await screen.findByText("Incorporation"))

  // confirm the transaction
  screen.getByText("Incorporer le lot", { selector: "h1" })
  userEvent.click(screen.getByText("Incorporer"))

  await screen.findByText("Incorporé")
})

test("accept sous reserve inbox lot from details", async () => {
  Data.set("lot-details", sentDetails)

  render(<LotDetailsWithRouter entity={operator} />)

  await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Demander une correction"))

  screen.getByText("Demander une correction", { selector: "h1" })
  userEvent.type(getField("Commentaire *"), "test is incorrect") // prettier-ignore
  userEvent.click(screen.getByText("Demander correction"))

  await screen.findByText("En correction")
})

test("reject inbox lot from details", async () => {
  Data.set("lot-details", sentDetails)

  render(<LotDetailsWithRouter entity={operator} />)

  await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Refuser"))

  // confirm the transaction
  screen.getByText("Refuser ce lot", { selector: "h1" })
  userEvent.type(getField("Commentaire *"), "not for me") // prettier-ignore
  userEvent.click(screen.getAllByText("Refuser")[1])

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
  checkGESFields()

  await screen.findByDisplayValue("Unknown Producer")

  const supplier = getField(/^Fournisseur/)
  expect(supplier).toHaveValue("Unknown Supplier")

  const supplierCertif = getField("Certificat du fournisseur")
  expect(supplierCertif).toHaveValue("ISCC2000 - Supplier")

  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")

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
  expect(getField(/^Fournisseur/)).toHaveValue("Producteur Test")
  expect(getField("Certificat du fournisseur")).toHaveValue("ISCC1000 - Vendor")
  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")
  expect(getField("Certificat du site de production")).toHaveValue(
    "2BS - KNOWN PSITE"
  )
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

  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  await screen.findByDisplayValue("Unknown Producer")
  expect(getField(/^Fournisseur/)).toHaveValue("Unknown Supplier")
  expect(getField("Certificat du fournisseur")).toHaveValue(
    "ISCC2000 - Supplier"
  )
  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")
  expect(getField("Certificat du site de production")).toHaveValue(
    "2BS - KNOWN PSITE"
  )
  expect(getField("Pays de production")).toHaveValue("France")
})
