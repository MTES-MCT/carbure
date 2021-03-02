import { render } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "common/components/relative-route"
import { Entity, LotStatus } from "common/types"

import { admin } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import Transactions from "../index"

import server, { setAdminLots } from "./api"
import { emptyLots } from "./data"

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
  setAdminLots(emptyLots)

  render(<TransactionsWithRouter status={LotStatus.Alert} entity={admin} />)

  await waitWhileLoading()

  screen.getByText("Alertes")
  screen.getByText("Corrections")
  screen.getByText("Lots déclarés")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Fournisseurs")
  screen.getByText("Clients")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucune transaction trouvée pour cette recherche")
})
