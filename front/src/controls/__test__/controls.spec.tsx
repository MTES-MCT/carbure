import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { AdminStatus } from "controls/types"

import { waitWhileLoading } from "common/__test__/helpers"
import Controls from "../index"

import server from "./api"
import useEntity from "carbure/hooks/entity"

const ControlsWithUser = () => {
  const entity = useEntity()
  if (entity.isAdmin || entity.isAuditor) return <Controls />
  else return null
}

const ControlsWithRouter = ({ status }: { status: AdminStatus }) => (
  <TestRoot url={`/org/3/controls/2021/${status}`}>
    <Route
      path="/org/:entity/controls/:year/:status/*"
      element={<ControlsWithUser />}
    />
  </TestRoot>
)

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("admin: display an empty list of transactions", async () => {
  render(<ControlsWithRouter status="alerts" />)

  await waitWhileLoading()

  await screen.findByText("Alerte")
  screen.getByText("Correction")
  screen.getByText("Déclaration")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Fournisseurs")
  screen.getByText("Clients")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucun résultat trouvé pour cette recherche")
})
