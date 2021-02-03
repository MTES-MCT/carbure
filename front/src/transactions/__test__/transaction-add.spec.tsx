import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "common/components/relative-route"
import { Entity } from "common/types"

import { producer } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import TransactionAdd from "../routes/transaction-add"

import server from "./api"

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const TransactionAddWithRouter = ({
  entity,
  refresh,
  children,
}: {
  entity: Entity
  children?: React.ReactNode
  refresh: () => {}
}) => (
  <MemoryRouter initialEntries={["/org/0/transactions/draft/add"]}>
    <Route path="/org/0/transactions/draft/add">
      <TransactionAdd entity={entity} refresh={refresh} />
    </Route>
    {children}
  </MemoryRouter>
)

test("display the transaction form", async () => {
  const refresh = jest.fn()

  render(<TransactionAddWithRouter entity={producer} refresh={refresh} />)

  screen.getByText("Créer une nouvelle transaction")
  screen.getByText("Brouillon")

  screen.getByLabelText("Il s'agit d'une mise à consommation ?")
  screen.getByLabelText("Numéro douanier (DAE, DAA...)")
  screen.getByLabelText("Volume en litres (Ethanol à 20°, autres à 15°)")
  screen.getByLabelText("Biocarburant")
  screen.getByLabelText("Matiere Premiere")
  screen.getByLabelText("Pays d'origine")
  screen.getByLabelText("Date de livraison")

  screen.getByLabelText("Producteur enregistré sur Carbure ?")
  screen.getByLabelText("Producteur")
  screen.getByLabelText("Site de production")
  screen.getByLabelText("Pays de production")
  screen.getByLabelText("Date de mise en service")
  screen.getByLabelText("N° d'enregistrement double-compte")
  screen.getByLabelText("Référence Système Fournisseur")

  screen.getByLabelText("Client enregistré sur Carbure ?")
  screen.getByLabelText("Client")
  screen.getByLabelText("Site de livraison enregistré sur Carbure ?")
  screen.getByLabelText("Site de livraison")
  screen.getByLabelText("Pays de livraison")
  screen.getByLabelText("Champ Libre")

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

  screen.getByText("Créer lot")
  screen.getByText("Retour")
})

test("check the form fields", async () => {
  const refresh = jest.fn()

  render(
    <TransactionAddWithRouter entity={producer} refresh={refresh}>
      <Route path="/org/0/transactions/draft/0">
        <span>LOT CREATED</span>
      </Route>
    </TransactionAddWithRouter>
  )

  userEvent.click(screen.getByLabelText("Il s'agit d'une mise à consommation ?")) // prettier-ignore
  userEvent.type(screen.getByLabelText("Numéro douanier (DAE, DAA...)"), "DAETEST") // prettier-ignore
  userEvent.type(
    screen.getByLabelText("Volume en litres (Ethanol à 20°, autres à 15°)"),
    "10000"
  )

  userEvent.type(screen.getByLabelText("Biocarburant"), "EM")
  userEvent.click(await screen.findByText("EMHV"))

  userEvent.type(screen.getByLabelText("Matiere Premiere"), "Co")
  userEvent.click(await screen.findByText("Colza"))

  userEvent.type(screen.getByLabelText("Pays d'origine"), "France")

  userEvent.type(screen.getByLabelText("Date de livraison"), "2020-31-12")

  screen.getByDisplayValue("Producteur Test")

  userEvent.type(screen.getByLabelText("Site de production"), "Test") // prettier-ignore
  userEvent.click(await screen.findByText("Test Production Site"))

  userEvent.type(screen.getByLabelText("Client"), "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))

  userEvent.type(screen.getByLabelText("Site de livraison"), "Test") // prettier-ignore
  userEvent.click(await screen.findByText("Test Delivery Site"))

  userEvent.type(screen.getByLabelText("Champ Libre"), "blabla")

  userEvent.type(screen.getByLabelText("EEC"), "10")
  userEvent.type(screen.getByLabelText("EL"), "1.1")
  userEvent.type(screen.getByLabelText("EP"), "1.2")
  userEvent.type(screen.getByLabelText("ETD"), "1.3")
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

test.todo("check the transaction form with entities that are not on carbure")
test.todo("check the transaction form defaults for operators")
