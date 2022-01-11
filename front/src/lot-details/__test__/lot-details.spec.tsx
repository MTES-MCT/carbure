import merge from "merge"
import { Route, Routes } from "react-router-dom"
import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Entity } from "common/types"

import { operator, producer } from "common/__test__/data"
import LotDetails from "../index"

import server, { setDetails } from "../../transactions/__test__/api"
import {
  lotDetails,
  errorDetails,
  sentDetails,
  tofixDetails,
  unknownProducerPartial,
  unknownProdSitePartial,
  noVendorPartial,
  operatorAuthorPartial,
  traderVendorPartial,
  stockPartial,
} from "../../transactions/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { clickOnCheckboxesAndConfirm } from "../../transactions/__test__/helpers"
import { okDynamicSettings, setEntity } from "settings/__test__/api"
import { PortalProvider } from "common-v2/components/portal"
import { okLotDetails, okUpdateLot } from "./api"

server.use(okDynamicSettings, okLotDetails, okUpdateLot)
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
beforeEach(() => {
  setDetails(lotDetails)
})
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const LotDetailsRoute = () => {
  return (
    <Routes>
      <Route path=":id" element={<LotDetails neighbors={[]} />} />
      <Route path="*" element={<h1>NOTHING</h1>} />
    </Routes>
  )
}

const LotDetailsWithRouter = ({ entity }: { entity: Entity }) => {
  setEntity(entity)
  return (
    <PortalProvider>
      <TestRoot url={`/org/${entity.id}/transactions/draft/0`}>
        <Route
          path="/org/:entity/transactions/:status/*"
          element={<LotDetailsRoute />}
        />
      </TestRoot>
    </PortalProvider>
  )
}

function getField(label: any) {
  const field = screen.getByText(label).parentElement?.querySelector("input")
  if (!field) throw new Error(`Cannot find field with label like ${label}`)
  return field
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

  await waitWhileLoading()

  screen.getByText("Détails du lot #TEST01")

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

  await waitWhileLoading()

  screen.getByText(/^Détails du lot/)

  const save: any = screen.getByText("Sauvegarder")

  const dae = getField("N° document d'accompagnement *")
  userEvent.clear(dae)
  userEvent.type(dae, "DAETESTUPDATE")

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

  await waitWhileLoading()

  userEvent.click(screen.getByText("Retour"))
}, 30000)

test.only("check transaction errors", async () => {
  setDetails(errorDetails)

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  await screen.findByText(
    (content, node) =>
      node?.textContent === "À valider avant le 29 février 2020"
  )

  const dae = screen.getByTitle("Le DAE (ou équivalent) est manquant")
  expect(dae).toHaveClass("errorLabel")

  const mp = screen.getByTitle("La matière première est manquante")
  expect(mp).toHaveClass("errorLabel")

  const errors = screen.getByText("Erreurs (2)")
  userEvent.click(errors)

  screen.getByText("Le DAE (ou équivalent) est manquant")
  screen.getByText("La matière première est manquante")

  const warnings = screen.getByText("Remarques (1)")
  userEvent.click(warnings)

  screen.getByText(
    "La matière première est incohérente avec le biocarburant - Biogaz de blé"
  )

  userEvent.click(screen.getByText("Retour"))
})

test("check transaction comments", async () => {
  setDetails(tofixDetails)

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("À corriger")

  const comments = screen.getByText("Commentaires (1)")
  userEvent.click(comments)

  screen.getByText("Opérateur Test:")
  screen.getByText("not ok")

  userEvent.type(
    screen.getByPlaceholderText("Entrez un commentaire..."),
    "test ok"
  )

  userEvent.click(screen.getByText("Envoyer"))

  await waitWhileLoading()

  await screen.findByText("Commentaires (2)")
  screen.getByText("Producteur Test:")
  screen.getByText("test ok")

  userEvent.click(screen.getByText("Retour"))
})

test("send draft lot from details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Envoyer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Envoyer lot")
  clickOnCheckboxesAndConfirm()

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  await screen.findByText("En attente")

  userEvent.click(screen.getByText("Retour"))
})

test("delete draft lot from details", async () => {
  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("Confirmer"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()
})

test("resend tofix lot from details", async () => {
  setDetails(tofixDetails)

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Renvoyer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Renvoyer le lot")
  userEvent.click(screen.getByText("Confirmer"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  await screen.findByText("Corrigé")

  const comments = screen.getByText("Commentaires (1)")
  userEvent.click(comments)

  userEvent.click(screen.getByText("Retour"))
})

test("delete tofix lot from details", async () => {
  setDetails(tofixDetails)

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("Confirmer"))

  await waitWhileLoading()
})

test("accept inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<LotDetailsWithRouter entity={operator} />)

  await waitWhileLoading()

  await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Accepter"))

  // confirm the transaction
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("Confirmer"))

  await waitWhileLoading()

  await screen.findByText("Accepté")

  userEvent.click(screen.getByText("Retour"))

  expect(screen.queryByText(/^Détails du lot/)).not.toBeInTheDocument()
})

test("accept sous reserve inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<LotDetailsWithRouter entity={operator} />)

  await waitWhileLoading()

  const status = await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Accepter sous réserve"))

  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("Les deux"))
  userEvent.type(getField("Commentaire (obligatoire)"), "test is incorrect") // prettier-ignore
  userEvent.click(screen.getByText("Confirmer"))

  await waitWhileLoading()

  userEvent.click(screen.getByText("Retour"))

  expect(status).not.toBeInTheDocument()
})

test("reject inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<LotDetailsWithRouter entity={operator} />)

  await waitWhileLoading()

  await screen.findByText("En attente")

  userEvent.click(await screen.findByText("Refuser"))

  // confirm the transaction
  screen.getByText("Refuser lot")
  userEvent.type(getField("Commentaire (obligatoire)"), "not for me") // prettier-ignore
  userEvent.click(screen.getByText("Confirmer"))

  await waitWhileLoading()
})

test("transaction details form as producer - producer trades unknown producer lot to operator", async () => {
  setDetails(
    merge.recursive(
      true,
      sentDetails,
      unknownProducerPartial,
      unknownProdSitePartial
    )
  )

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  expect(getField(/^Producteur/)).toHaveValue("Unknown Producer")

  const supplier = getField(/^Fournisseur/)
  expect(supplier).toHaveValue("Unknown Supplier")

  const supplierCertif = getField("Certificat du fournisseur")
  expect(supplierCertif).toHaveValue("ISCC2000 - Supplier")

  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")

  const certif = getField("Certificat du site de production")
  expect(certif).toHaveValue("2BS - PSITE")

  const psiteCountry = getField("Pays de production")
  expect(psiteCountry).toHaveValue("France")

  expect(getField("Votre certificat")).toHaveValue("ISCC1000 - Vendor")
})

test("transaction details form as operator - producer trades unknown producer lot to operator", async () => {
  setDetails(
    merge.recursive(
      true,
      sentDetails,
      unknownProducerPartial,
      unknownProdSitePartial
    )
  )

  render(<LotDetailsWithRouter entity={operator} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  expect(getField(/^Producteur/)).toHaveValue("Unknown Producer")
  expect(getField(/^Fournisseur/)).toHaveValue("Producteur Test")
  expect(getField("Certificat du fournisseur")).toHaveValue("ISCC1000 - Vendor")
  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")
  expect(getField("Certificat du site de production")).toHaveValue(
    "2BS - PSITE"
  )
  expect(getField("Pays de production")).toHaveValue("France")
})

test("transaction details form as operator - operator self accepts lot", async () => {
  setDetails(
    merge.recursive(
      true,
      sentDetails,
      unknownProducerPartial,
      unknownProdSitePartial,
      noVendorPartial,
      operatorAuthorPartial
    )
  )

  render(<LotDetailsWithRouter entity={operator} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  expect(getField(/^Producteur/)).toHaveValue("Unknown Producer")
  expect(getField(/^Fournisseur/)).toHaveValue("Unknown Supplier")
  expect(getField("Certificat du fournisseur")).toHaveValue(
    "ISCC2000 - Supplier"
  )
  expect(getField(/^Site de production/)).toHaveValue("Unknown Production Site")
  expect(getField("Certificat du site de production")).toHaveValue(
    "2BS - PSITE"
  )
  expect(getField("Pays de production")).toHaveValue("France")
})

test("transaction details form as producer - lot coming back for correction after being sold by trader after buying from producer", async () => {
  setDetails(
    merge.recursive(true, sentDetails, traderVendorPartial, stockPartial)
  )

  render(<LotDetailsWithRouter entity={producer} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  expect(getField(/^Producteur/)).toHaveValue("Producteur Test")

  const vendor = getField(/Fournisseur/)
  expect(vendor).toHaveValue("Unknown Supplier")

  const certificate = getField(/Certificat du fournisseur/)
  expect(certificate).toHaveValue("ISCC2000 - Supplier")

  expect(getField(/^Site de production/)).toHaveValue("Test Production Site")
  expect(getField("Certificat du site de production")).toHaveValue(
    "2BS - KNOWN PSITE"
  )
  expect(getField("Pays de production")).toHaveValue("France")
})
