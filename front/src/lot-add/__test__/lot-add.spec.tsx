import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { operator, producer, trader } from "common-v2/__test__/data"
import { getField, waitWhileLoading } from "common-v2/__test__/helpers"
import LotAdd from "../index"

import { PortalProvider } from "common-v2/components/portal"
import { setEntity } from "settings/__test__/api"
import server from "./api"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const TransactionAddWithRouter = ({
  entityID = 0,
  children,
}: {
  entityID?: number
  children?: React.ReactNode
}) => (
  <PortalProvider>
    <TestRoot url={`/org/${entityID}/transactions/draft/pending/add`}>
      <Route
        path="/org/:entity/transactions/draft/pending/add"
        element={<LotAdd />}
      />
      {children}
    </TestRoot>
  </PortalProvider>
)

function checkLotFields() {
  getField("N° document d'accompagnement")
  getField("Volume en litres")
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
  getField("Émissions")
  getField("EEC")
  getField("EL")
  getField("EP")
  getField("ETD")
  getField("EU")

  getField("Réductions")
  getField("ESCA")
  getField("ECCS")
  getField("ECCR")
  getField("EEE")

  getField("Total")
  getField("Réd. RED I")
}

test("display the transaction form - producer with trading and mac", async () => {
  render(<TransactionAddWithRouter />)

  await screen.findByText("Créer un nouveau lot")
  screen.getByText("Brouillon")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  screen.getByText("Créer lot")
  screen.getByText("Retour")
})

test("display the transaction form - pure producer", async () => {
  setEntity({ ...producer, has_trading: false, has_mac: false })
  render(<TransactionAddWithRouter />)

  // await waitWhileLoading()

  await screen.findByText("Créer un nouveau lot")

  checkLotFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  const prodField = await screen.findAllByDisplayValue(/^Producteur/)
  expect(prodField[0]).toBeDisabled()
  expect(prodField[0]).toHaveValue(producer.name)
})

test("display the transaction form - operator", async () => {
  setEntity(operator)
  render(<TransactionAddWithRouter entityID={operator.id} />)

  // await waitWhileLoading()
  await screen.findByText("Créer un nouveau lot")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  await screen.findByDisplayValue(operator.name)
})

test("display the transaction form - trader", async () => {
  setEntity(trader)
  render(<TransactionAddWithRouter entityID={trader.id} />)

  // await waitWhileLoading()
  await screen.findByText("Créer un nouveau lot")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()
})

test("check the form fields are working", async () => {
  setEntity(producer)
  render(
    <TransactionAddWithRouter entityID={producer.id}>
      <Route path="/drafts/imported/0" element={<span>LOT CREATED</span>} />
    </TransactionAddWithRouter>
  )

  // await waitWhileLoading()
  await screen.findByText("Créer un nouveau lot")

  userEvent.type(getField("N° document d'accompagnement"), "DAETEST") // prettier-ignore
  userEvent.type(getField("Volume en litres"), "10000") // prettier-ignore

  userEvent.type(getField("Biocarburant"), "EM")
  userEvent.click(await screen.findByText("EMHV"))
  await screen.findByDisplayValue("EMHV")

  userEvent.type(getField("Matière première"), "Co")
  userEvent.click(await screen.findByText("Colza"))
  await screen.findByDisplayValue("Colza")

  userEvent.type(getField("Pays d'origine de la matière première"), "France")
  await waitWhileLoading()

  userEvent.type(getField("Date de livraison"), "2020-31-12")

  userEvent.type(getField("Producteur"), "Pr")
  userEvent.click(await screen.findByText("Producteur Test"))
  const producerFields = await screen.findAllByDisplayValue("Producteur Test")
  expect(producerFields).toHaveLength(2)

  userEvent.type(getField("Site de production"), "Test")
  userEvent.click(await screen.findByText("Test Production Site"))
  await screen.findByDisplayValue("Test Production Site")

  const psiteCountry = getField("Pays de production")
  const psiteComDate = getField("Date de mise en service")
  // const psiteDC = getField("Certificat double-comptage")

  expect(psiteCountry).toBeDisabled()
  expect(psiteCountry).toHaveValue("France")
  // expect(psiteDC).toBeDisabled()
  expect(psiteComDate).toBeDisabled()
  expect(psiteComDate).toHaveValue("2000-01-31")

  userEvent.type(getField("Client"), "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))
  await screen.findByDisplayValue("Opérateur Test")

  expect(getField("Pays de livraison")).not.toBeDisabled()

  userEvent.type(getField("Site de livraison"), "Test") // prettier-ignore
  userEvent.click(await screen.findByText("Test Delivery Site"))
  await screen.findByDisplayValue("Test Delivery Site")

  expect(getField("Pays de livraison")).toBeDisabled()

  userEvent.type(getField("Champ libre"), "blabla")

  userEvent.type(getField("EEC"), "10")
  userEvent.type(getField("EL"), "1.1")
  userEvent.type(getField("EP"), "1.2")
  userEvent.type(getField("ETD"), "1.3")
  userEvent.type(getField("EU"), "1.4")

  userEvent.type(getField("ESCA"), "1.1")
  userEvent.type(getField("ECCS"), "1.2")
  userEvent.type(getField("ECCR"), "1.3")
  userEvent.type(getField("EEE"), "1.4")

  userEvent.click(screen.getByText("Créer lot"))

  // await waitWhileLoading()

  // page for the newly created lot appears
  await screen.findByText("LOT CREATED")

  // creation form disappears
  expect(
    screen.queryByText("Créer une nouvelle transaction")
  ).not.toBeInTheDocument()
}, 30000)
