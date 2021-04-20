import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "common/components/relative-route"
import { Entity } from "common/types"

import { operator, producer, trader } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import TransactionAdd from "../routes/transaction-add"

import server from "./api"

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const TransactionAddWithRouter = ({
  entity,
  children,
  refresh = () => {},
}: {
  entity: Entity
  children?: React.ReactNode
  refresh?: () => void
}) => (
  <MemoryRouter initialEntries={["/org/0/transactions/draft/add"]}>
    <Route path="/org/0/transactions/draft/add">
      <TransactionAdd entity={entity} refresh={refresh} />
    </Route>
    {children}
  </MemoryRouter>
)

function checkLotFields() {
  screen.getByLabelText("Numéro douanier (DAE, DAA...) *")
  screen.getByLabelText("Volume en litres (Ethanol à 20°, autres à 15°) *")
  screen.getByLabelText("Biocarburant *")
  screen.getByLabelText("Matiere premiere *")
  screen.getByLabelText("Pays d'origine de la matière première *")
  screen.getByLabelText("Date de livraison")
}

function checkProductionFields() {
  screen.getByLabelText("Site de production")
  screen.getByLabelText("Certificat du site de production")
  screen.getByLabelText("Pays de production")
  screen.getByLabelText("Date de mise en service *")
  screen.getByLabelText("N° d'enregistrement double-compte")
}

function checkOriginFields() {
  screen.getByLabelText("Producteur")
  screen.getByLabelText("Fournisseur")
  screen.getByLabelText("Certificat du fournisseur")
  screen.getByLabelText("Champ libre")
}

function checkDeliveryFields() {
  screen.getByLabelText("Client")
  screen.getByLabelText("Site de livraison *")
  screen.getByLabelText("Pays de livraison *")
}

function checkGESFields() {
  screen.getByText("Émissions")
  screen.getByLabelText("EEC")
  screen.getByLabelText("EL")
  screen.getByLabelText("EP *")
  screen.getByLabelText("ETD *")
  screen.getByLabelText("EU")

  screen.getByText("Réductions")
  screen.getByLabelText("ESCA")
  screen.getByLabelText("ECCS")
  screen.getByLabelText("ECCR")
  screen.getByLabelText("EEE")

  screen.getByLabelText("Total")
  screen.getByLabelText("Réduction")
}

test("display the transaction form - producer with trading and mac", async () => {
  render(<TransactionAddWithRouter entity={producer} />)

  screen.getByText("Créer une nouvelle transaction")
  screen.getByText("Brouillon")

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  screen.getByText("Il s'agit d'une mise à consommation ?")
  screen.getByLabelText("Votre certificat *")

  screen.getByText("Créer lot")
  screen.getByText("Retour")
})

test("display the transaction form - pure producer", async () => {
  const entity = { ...producer, has_trading: false, has_mac: false }
  render(<TransactionAddWithRouter entity={entity} />)

  checkLotFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  const prodField = screen.getByLabelText("Producteur")
  expect(prodField).toBeDisabled()
  expect(prodField).toHaveValue(entity.name)

  expect(screen.getByLabelText("Fournisseur")).toBeDisabled()
  expect(screen.getByLabelText("Certificat du fournisseur")).toBeDisabled()
})

test("display the transaction form - operator", async () => {
  render(<TransactionAddWithRouter entity={operator} />)

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  const client = screen.getByLabelText("Client")
  expect(client).toBeDisabled()
  expect(client).toHaveValue(operator.name)
})

test("display the transaction form - trader", async () => {
  render(<TransactionAddWithRouter entity={trader} />)

  checkLotFields()
  checkOriginFields()
  checkProductionFields()
  checkDeliveryFields()
  checkGESFields()

  screen.getByText("Il s'agit d'une mise à consommation ?")
  screen.getByLabelText("Votre certificat *")
})

test("check the form fields are working", async () => {
  const refresh = jest.fn()

  render(
    <TransactionAddWithRouter entity={producer} refresh={refresh}>
      <Route path="/org/0/transactions/draft/0">
        <span>LOT CREATED</span>
      </Route>
    </TransactionAddWithRouter>
  )

  userEvent.type(screen.getByLabelText("Numéro douanier (DAE, DAA...) *"), "DAETEST") // prettier-ignore
  userEvent.type(screen.getByLabelText("Volume en litres (Ethanol à 20°, autres à 15°) *"), "10000") // prettier-ignore

  userEvent.type(screen.getByLabelText("Biocarburant *"), "EM")
  userEvent.click(await screen.findByText("EMHV"))

  userEvent.type(screen.getByLabelText("Matiere premiere *"), "Co")
  userEvent.click(await screen.findByText("Colza"))

  userEvent.type(
    screen.getByLabelText("Pays d'origine de la matière première *"),
    "France"
  )

  userEvent.type(screen.getByLabelText("Date de livraison"), "2020-31-12")

  userEvent.type(screen.getByLabelText("Producteur"), "Pr")
  userEvent.click(await screen.findByText("Producteur Test"))

  expect(screen.getByLabelText("Fournisseur")).toBeDisabled()
  expect(screen.getByLabelText("Certificat du fournisseur")).toBeDisabled()

  userEvent.type(screen.getByLabelText("Site de production"), "Test") // prettier-ignore
  userEvent.click(await screen.findByText("Test Production Site"))

  const psiteCountry = screen.getByLabelText("Pays de production")
  const psiteComDate = screen.getByLabelText("Date de mise en service *")
  const psiteDC = screen.getByLabelText("N° d'enregistrement double-compte")

  expect(psiteCountry).toBeDisabled()
  expect(psiteCountry).toHaveValue("France")
  expect(psiteDC).toBeDisabled()
  expect(psiteComDate).toBeDisabled()
  expect(psiteComDate).toHaveValue("2000-01-31")

  userEvent.type(screen.getByLabelText("Client"), "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))

  const dsite = screen.getByLabelText("Site de livraison *")
  const dsiteCountry = screen.getByLabelText("Pays de livraison *")

  expect(dsiteCountry).not.toBeDisabled()

  userEvent.type(dsite, "Test") // prettier-ignore
  userEvent.click(await screen.findByText("Test Delivery Site"))

  expect(dsiteCountry).toBeDisabled()

  userEvent.type(screen.getByLabelText("Champ libre"), "blabla")

  userEvent.click(screen.getByText("Oui"))
  expect(dsite).toBeDisabled()

  userEvent.type(screen.getByLabelText("EEC"), "10")
  userEvent.type(screen.getByLabelText("EL"), "1.1")
  userEvent.type(screen.getByLabelText("EP *"), "1.2")
  userEvent.type(screen.getByLabelText("ETD *"), "1.3")
  userEvent.type(screen.getByLabelText("EU"), "1.4")

  userEvent.type(screen.getByLabelText("ESCA"), "1.1")
  userEvent.type(screen.getByLabelText("ECCS"), "1.2")
  userEvent.type(screen.getByLabelText("ECCR"), "1.3")
  userEvent.type(screen.getByLabelText("EEE"), "1.4")

  userEvent.click(screen.getByText("Créer lot"))

  await waitWhileLoading()

  // creation form disappears
  expect(
    screen.queryByText("Créer une nouvelle transaction")
  ).not.toBeInTheDocument()

  // page for the newly created lot appears
  await screen.findByText("LOT CREATED")

  expect(refresh).toHaveBeenCalledTimes(1)
})
