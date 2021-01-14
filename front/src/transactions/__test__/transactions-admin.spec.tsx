import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "common/components/relative-route"
import { Entity, LotStatus } from "common/types"

import { admin } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import Transactions from "../index"

import server, { setLots, setSnapshot } from "./api"
import { emptyLots, adminSnapshot } from "./data"

const TransactionsWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: LotStatus
}) => (
  <MemoryRouter initialEntries={[`/org/0/transactions/${status}`]}>
    <Route path="/org/0/transactions/:status">
      <Transactions entity={entity} />
    </Route>
  </MemoryRouter>
)

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => server.close())

test("operator: display an empty list of transactions", async () => {
  setSnapshot(adminSnapshot)
  setLots(emptyLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={admin} />)

  await waitWhileLoading()

  // screen.getByText("Alertes")
  // screen.getByText("Corrections")
  // screen.getByText("Déclarations")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  // screen.getByText("Producteurs")
  // screen.getByText("Trader")
  // screen.getByText("Opérateur")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucune transaction trouvée pour ces paramètres")
})
