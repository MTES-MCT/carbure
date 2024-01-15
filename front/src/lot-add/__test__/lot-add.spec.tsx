import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { operator, producer, trader } from "carbure/__test__/data"
import { getField, setEntity } from "carbure/__test__/helpers"
import LotAdd from "../index"

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
  <TestRoot url={`/org/${entityID}/transactions/draft/pending/add`}>
    <Route
      path="/org/:entity/transactions/draft/pending/add"
      element={<LotAdd />}
    />
    {children}
  </TestRoot>
)

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
  const user = userEvent.setup()

  setEntity(producer)
  render(
    <TransactionAddWithRouter entityID={producer.id}>
      <Route path="/drafts/imported/0" element={<span>LOT CREATED</span>} />
    </TransactionAddWithRouter>
  )

  // await waitWhileLoading()
  await screen.findByText("Créer un nouveau lot")

  await user.type(getField("N° document d'accompagnement"), "DAETEST") // prettier-ignore
  await user.type(getField("Quantité"), "10000") // prettier-ignore

  await user.type(getField("Biocarburant"), "EM")
  await user.click(await screen.findByText("EMHV"))
  await screen.findByDisplayValue("EMHV")

  await user.type(getField("Matière première"), "Co")
  await user.click(await screen.findByText("Colza"))
  await screen.findByDisplayValue("Colza")

  await user.type(getField("Pays d'origine de la matière première"), "France")

  await user.type(getField("Date de livraison"), "2020-31-12")

  await user.type(getField("Producteur"), "Pr")
  await user.click(await screen.findByText("Producteur Test"))
  const producerFields = await screen.findAllByDisplayValue("Producteur Test")
  expect(producerFields).toHaveLength(2)

  await user.type(getField("Site de production"), "Test")
  await user.click(await screen.findByText("Test Production Site"))
  await screen.findByDisplayValue("Test Production Site")

  const psiteCountry = getField("Pays de production")
  const psiteComDate = getField("Date de mise en service")
  // const psiteDC = getField("Certificat double-comptage")

  expect(psiteCountry).toBeDisabled()
  expect(psiteCountry).toHaveValue("France")
  // expect(psiteDC).toBeDisabled()
  expect(psiteComDate).toBeDisabled()
  expect(psiteComDate).toHaveValue("2000-01-31")

  await user.type(getField("Client"), "Test")
  await user.click(await screen.findByText("Opérateur Test"))
  await screen.findByDisplayValue("Opérateur Test")

  expect(getField("Pays de livraison")).not.toBeDisabled()

  await user.type(getField("Site de livraison"), "Test") // prettier-ignore
  await user.click(await screen.findByText("Test Delivery Site"))
  await screen.findByDisplayValue("Test Delivery Site")

  expect(getField("Pays de livraison")).toBeDisabled()

  await user.type(getField("Champ libre"), "blabla")

  await user.type(getField("EEC"), "10")
  await user.type(getField("EL"), "1.1")
  await user.type(getField("EP"), "1.2")
  await user.type(getField("ETD"), "1.3")
  await user.type(getField("EU"), "1.4")

  await user.type(getField("ESCA"), "1.1")
  await user.type(getField("ECCS"), "1.2")
  await user.type(getField("ECCR"), "1.3")
  await user.type(getField("EEE"), "1.4")

  await user.click(screen.getByText("Créer lot"))

  // await waitWhileLoading()

  // page for the newly created lot appears
  await screen.findByText("LOT CREATED")

  // creation form disappears
  expect(
    screen.queryByText("Créer une nouvelle transaction")
  ).not.toBeInTheDocument()
}, 30000)
