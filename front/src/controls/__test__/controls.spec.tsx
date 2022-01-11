import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { Entity, LotStatus } from "common/types"

import { admin } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import Controls from "../index"

import server, { setAdminLots } from "transactions/__test__/api"
import { emptyLots } from "transactions/__test__/data"

const ControlsWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: LotStatus
}) => (
  <TestRoot url={`/org/0/controls/${status}`}>
    <Route path="/org/0/controls/:status/*" element={<Controls />} />
  </TestRoot>
)

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

afterEach(() => {
  server.resetHandlers()
})

afterAll(() => server.close())

test("admin: display an empty list of transactions", async () => {
  setAdminLots(emptyLots)

  render(<ControlsWithRouter status={LotStatus.Alert} entity={admin} />)

  await waitWhileLoading()

  screen.getByText("Alerte")
  screen.getByText("Correction")
  screen.getByText("Lot déclaré")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Fournisseurs")
  screen.getByText("Clients")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher des lots...")

  screen.getByText("Aucune transaction trouvée pour cette recherche")
})
