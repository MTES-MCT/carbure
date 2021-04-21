import merge from "merge"
import { render } from "setupTests"
import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { Route } from "common/components/relative-route"
import { Entity } from "common/types"

import { operator, producer } from "common/__test__/data"
import { useTransactions } from "../index"
import TransactionDetails from "../routes/transaction-details"

import server, { setDetails } from "./api"
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
} from "./data"
import { waitWhileLoading } from "common/__test__/helpers"
import { clickOnCheckboxesAndConfirm } from "./helpers"

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  setDetails(lotDetails)
})
afterAll(() => server.close())

const TransactionWithHook = ({ entity }: { entity: Entity }) => {
  const {
    transactions,
    deleter,
    validator,
    acceptor,
    rejector,
    refresh,
  } = useTransactions(entity)

  return (
    <Route relative path=":id">
      <TransactionDetails
        entity={entity}
        refresh={refresh}
        deleter={deleter}
        validator={validator}
        acceptor={acceptor}
        rejector={rejector}
        transactions={transactions}
      />
    </Route>
  )
}

const TransactionWithRouter = ({ entity }: { entity: Entity }) => (
  <MemoryRouter initialEntries={["/org/0/transactions/draft/0"]}>
    <Route path="/org/0/transactions/:status">
      <TransactionWithHook entity={entity} />
    </Route>
  </MemoryRouter>
)

function checkLotFields() {
  screen.getByLabelText("Numéro douanier (DAE, DAA...)")
  screen.getByLabelText("Volume en litres (Ethanol à 20°, autres à 15°)")
  screen.getByLabelText("Biocarburant")
  screen.getByLabelText("Matiere premiere")
  screen.getByLabelText("Pays d'origine de la matière première")
}

function checkProductionFields() {
  screen.getByLabelText("Site de production")
  screen.getByLabelText("Certificat du site de production")
  screen.getByLabelText("Pays de production")
  screen.getByLabelText("Date de mise en service")
  screen.getByLabelText("N° d'enregistrement double-compte")
}

function checkOriginFields() {
  screen.getByLabelText("Producteur")
  screen.getAllByLabelText("Fournisseur")
  screen.getAllByLabelText("Certificat du fournisseur")
  screen.getByLabelText("Champ libre")
}

function checkDeliveryFields() {
  screen.getByLabelText("Client")
  screen.getByLabelText("Site de livraison")
  screen.getByLabelText("Pays de livraison")
  screen.getByLabelText("Date de livraison")
}

function checkGESFields() {
  screen.getByText("Émissions")
  screen.getByLabelText("EEC")
  screen.getByLabelText("EL")
  screen.getByLabelText("EP")
  screen.getByLabelText("ETD")
  screen.getByLabelText("EU")

  screen.getByText("Réductions")
  screen.getByLabelText("ESCA")
  screen.getByLabelText("ECCS")
  screen.getByLabelText("ECCR")
  screen.getByLabelText("EEE")

  screen.getByLabelText("Total")
  screen.getByLabelText("Réduction")
}

test("display transaction details", async () => {
  render(<TransactionWithRouter entity={producer} />)

  const title = screen.getByText("Détails de la transaction")

  await waitWhileLoading()

  await screen.findByDisplayValue("DAETEST")

  screen.getByDisplayValue("12345")
  screen.getByDisplayValue("EMHV")
  screen.getByDisplayValue("Colza")
  screen.getByDisplayValue("2020-01-31")
  screen.getByDisplayValue("Producteur Test")
  screen.getByDisplayValue("Test Production Site")
  screen.getByDisplayValue("2000-01-31")
  screen.getByDisplayValue("Opérateur Test")
  screen.getByDisplayValue("Test Delivery Site")
  screen.getByDisplayValue("12")
  screen.getByDisplayValue("1")
  screen.getByDisplayValue("11.00 gCO2eq/MJ")
  screen.getByDisplayValue("86.87%")

  const countries = screen.getAllByDisplayValue("France")
  const zeros = screen.getAllByDisplayValue("0")

  expect(countries.length).toBe(3)
  expect(zeros.length).toBe(7)

  userEvent.click(screen.getByText("Retour"))

  expect(title).not.toBeInTheDocument()
})

test("edit transaction details", async () => {
  render(<TransactionWithRouter entity={producer} />)

  const title = screen.getByText("Détails de la transaction")

  await waitWhileLoading()

  const save: any = await screen.findByText("Sauvegarder")
  expect(save.closest("button")).toBeDisabled()

  const dae = screen.getByLabelText("Numéro douanier (DAE, DAA...) *")
  userEvent.clear(dae)
  userEvent.type(dae, "DAETESTUPDATE")

  const vol = screen.getByLabelText(
    "Volume en litres (Ethanol à 20°, autres à 15°) *"
  )
  userEvent.clear(vol)
  userEvent.type(vol, "20000")

  const bio = screen.getByLabelText("Biocarburant *")
  userEvent.clear(bio)
  userEvent.type(bio, "EM")
  userEvent.click(await screen.findByText("EMHV"))

  const mp = screen.getByLabelText("Matiere premiere *")
  userEvent.clear(mp)
  userEvent.type(mp, "Co")
  userEvent.click(await screen.findByText("Colza"))

  const ct: any = screen.getByLabelText(
    "Pays d'origine de la matière première *"
  )
  userEvent.clear(ct)
  userEvent.type(ct, "Fra")
  userEvent.click(await screen.findByText("France"))

  const dd = screen.getByLabelText("Date de livraison")
  userEvent.clear(dd)
  userEvent.type(dd, "2021-31-01")

  const prod = screen.getByDisplayValue("Producteur Test")

  const ps = screen.getByLabelText("Site de production")
  userEvent.clear(ps)
  userEvent.type(ps, "Test")
  userEvent.click(await screen.findByText("Test Production Site"))

  const cli = screen.getByLabelText("Client")
  userEvent.clear(cli)
  userEvent.type(cli, "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))

  const ds = screen.getByLabelText("Site de livraison *")
  userEvent.clear(ds)
  userEvent.type(ds, "Test")
  userEvent.click(await screen.findByText("Test Delivery Site"))

  const cl = screen.getByLabelText("Champ libre")
  userEvent.clear(cl)
  userEvent.type(cl, "blabla")

  const eec = screen.getByLabelText("EEC")
  userEvent.clear(eec)
  userEvent.type(eec, "10")

  const el = screen.getByLabelText("EL")
  userEvent.clear(el)
  userEvent.type(el, "1.1")

  const ep = screen.getByLabelText("EP *")
  userEvent.clear(ep)
  userEvent.type(ep, "1.2")

  const etd = screen.getByLabelText("ETD *")
  userEvent.clear(etd)
  userEvent.type(etd, "1.3")

  const eu = screen.getByLabelText("EU")
  userEvent.clear(eu)
  userEvent.type(eu, "1.4")

  const esca = screen.getByLabelText("ESCA")
  userEvent.clear(esca)
  userEvent.type(esca, "1.1")

  const eccs = screen.getByLabelText("ECCS")
  userEvent.clear(eccs)
  userEvent.type(eccs, "1.2")

  const eccr = screen.getByLabelText("ECCR")
  userEvent.clear(eccr)
  userEvent.type(eccr, "1.3")

  const eee = screen.getByLabelText("EEE")
  userEvent.clear(eee)
  userEvent.type(eee, "1.4")

  expect(save.closest("button")).not.toBeDisabled()
  // expect(save.disabled).toBe(false)

  userEvent.click(save)

  await waitWhileLoading()

  await screen.findByDisplayValue("DAETESTUPDATE OK")

  userEvent.click(screen.getByText("Retour"))
  await waitFor(() => expect(title).not.toBeInTheDocument())
})

test("check transaction errors", async () => {
  setDetails(errorDetails)

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()

  await screen.findByText(
    (content, node) =>
      node?.textContent === "Ce lot doit être validé avant le 29 février 2020"
  )

  const dae = screen.getByTitle("DAE manquant")
  expect(dae).toHaveClass("errorLabel")

  const mp = screen.getByTitle("Merci de préciser la matière première")
  expect(mp).toHaveClass("errorLabel")

  screen.getByText("Erreurs (3)")
  screen.getByText(
    "Matière Première incohérente avec le Biocarburant - Biogaz de Blé"
  )
  screen.getByText("DAE manquant")
  screen.getByText("Merci de préciser la matière première")

  screen.getByText("Remarques (1)")
  screen.getByText("Volume inhabituellement faible.")

  userEvent.click(screen.getByText("Retour"))
})

test("check transaction comments", async () => {
  setDetails(tofixDetails)

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("À corriger")

  screen.getByText("Commentaires (1)")
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
  render(<TransactionWithRouter entity={producer} />)

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
  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitForElementToBeRemoved(() =>
    screen.getByText("Détails de la transaction")
  )
})

test("resend tofix lot from details", async () => {
  setDetails(tofixDetails)

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Renvoyer")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Envoyer lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "test is fixed") // prettier-ignore
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  await screen.findByText("Corrigé")
  screen.getByText("Commentaires (2)")
  screen.getByText("test is fixed")

  userEvent.click(screen.getByText("Retour"))
})

test("delete tofix lot from details", async () => {
  setDetails(tofixDetails)

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByText("Supprimer")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  await waitForElementToBeRemoved(() =>
    screen.getByText("Détails de la transaction")
  )
})

test("accept inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<TransactionWithRouter entity={operator} />)

  await waitWhileLoading()

  await screen.findByText("En attente")

  userEvent.click(screen.getByText("Accepter"))

  // confirm the transaction
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("OK"))

  await waitWhileLoading()

  await screen.findByText("Accepté")

  userEvent.click(screen.getByText("Retour"))

  expect(
    screen.queryByText("Détails de la transaction")
  ).not.toBeInTheDocument()
})

test("accept sous reserve inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<TransactionWithRouter entity={operator} />)

  await waitWhileLoading()

  const status = await screen.findByText("En attente")

  userEvent.click(screen.getByText("Accepter sous réserve"))

  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("Les deux"))
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "test is incorrect") // prettier-ignore
  userEvent.click(screen.getByText("Accepter et demander une correction"))

  await waitWhileLoading()

  userEvent.click(screen.getByText("Retour"))

  expect(status).not.toBeInTheDocument()
})

test("reject inbox lot from details", async () => {
  setDetails(sentDetails)

  render(<TransactionWithRouter entity={operator} />)

  await waitWhileLoading()

  await screen.findByText("En attente")

  userEvent.click(screen.getByText("Refuser"))

  // confirm the transaction
  screen.getByText("Refuser lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "not for me") // prettier-ignore
  userEvent.click(screen.getByText("OK"))

  await waitForElementToBeRemoved(() =>
    screen.queryByText("Détails de la transaction")
  )
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

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()

  expect(screen.getByLabelText("Producteur")).toHaveValue("Unknown Producer")

  const supplier = screen.getByLabelText("Fournisseur")
  expect(supplier).toHaveValue("Unknown Supplier")

  const supplierCertif = screen.getByLabelText("Certificat du fournisseur")
  expect(supplierCertif).toHaveValue("ISCC2000 - Supplier")

  expect(screen.getByLabelText("Site de production")).toHaveValue(
    "Unknown Production Site"
  )

  const certif = screen.getByLabelText("Certificat du site de production")
  expect(certif).toHaveValue("2BS - PSITE")

  const psiteCountry = screen.getByLabelText("Pays de production")
  expect(psiteCountry).toHaveValue("France")

  expect(screen.getByLabelText("Votre certificat")).toHaveValue(
    "ISCC1000 - Vendor"
  )
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

  render(<TransactionWithRouter entity={operator} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()

  expect(screen.getByLabelText("Producteur")).toHaveValue("Unknown Producer")
  expect(screen.getByLabelText("Fournisseur")).toHaveValue("Producteur Test")
  expect(screen.getByLabelText("Certificat du fournisseur")).toHaveValue(
    "ISCC1000 - Vendor"
  )
  expect(screen.getByLabelText("Site de production")).toHaveValue(
    "Unknown Production Site"
  )
  expect(screen.getByLabelText("Certificat du site de production")).toHaveValue(
    "2BS - PSITE"
  )
  expect(screen.getByLabelText("Pays de production")).toHaveValue("France")
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

  render(<TransactionWithRouter entity={operator} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()

  expect(screen.getByLabelText("Producteur")).toHaveValue("Unknown Producer")
  expect(screen.getByLabelText("Fournisseur")).toHaveValue("Unknown Supplier")
  expect(screen.getByLabelText("Certificat du fournisseur")).toHaveValue(
    "ISCC2000 - Supplier"
  )
  expect(screen.getByLabelText("Site de production")).toHaveValue(
    "Unknown Production Site"
  )
  expect(screen.getByLabelText("Certificat du site de production")).toHaveValue(
    "2BS - PSITE"
  )
  expect(screen.getByLabelText("Pays de production")).toHaveValue("France")
})

test("transaction details form as producer - lot sold by trader after buying from producer", async () => {
  setDetails(
    merge.recursive(true, sentDetails, traderVendorPartial, stockPartial)
  )

  render(<TransactionWithRouter entity={producer} />)

  await waitWhileLoading()
  await screen.findByDisplayValue("DAETEST")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()

  expect(screen.getByLabelText("Producteur")).toHaveValue("Producteur Test")

  const vendors = screen.getAllByLabelText("Fournisseur")
  expect(vendors[0]).toHaveValue("Unknown Supplier")
  expect(vendors[1]).toHaveValue("Trader Test")

  const certificates = screen.getAllByLabelText("Certificat du fournisseur")
  expect(certificates[0]).toHaveValue("ISCC2000 - Supplier")
  expect(certificates[1]).toHaveValue("ISCC1000 - Vendor")

  expect(screen.getByLabelText("Site de production")).toHaveValue(
    "Test Production Site"
  )
  expect(screen.getByLabelText("Certificat du site de production")).toHaveValue(
    "2BS - KNOWN PSITE"
  )
  expect(screen.getByLabelText("Pays de production")).toHaveValue("France")
})
