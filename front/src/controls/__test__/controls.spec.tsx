import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { AdminStatus } from "controls/types"
import userEvent from "@testing-library/user-event"

import { waitWhileLoading } from "carbure/__test__/helpers"
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
  await screen.findByText("Signalement")
  screen.getByText("Lot")
  screen.getByText("Stock")
  screen.getByText("Statut")
  screen.getByText("Corrections")
  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Pays d'origine")
  screen.getByText("Fournisseurs")
  screen.getByText("Clients")
  screen.getByText("Types de client")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")
  screen.getByText("Ajouté par")
  screen.getByText("Incohérences")
  screen.getByText("Conformité")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucun résultat trouvé pour cette recherche")
})

test("admin: display an empty list of lots", async () => {
  render(<ControlsWithRouter status="alerts" />)
  const user = userEvent.setup()
  await waitWhileLoading()
  const link = await screen.findByText("Lot")
  await user.click(link.closest("a")!)
  screen.getByText("Aucun résultat trouvé pour cette recherche")
  await waitWhileLoading()
})

test("admin: display an empty list of stocks", async () => {
  render(<ControlsWithRouter status="alerts" />)
  const user = userEvent.setup()
  await waitWhileLoading()
  const link = await screen.findByText("Stock")
  await user.click(link.closest("a")!)
  screen.getByText("Aucun résultat trouvé pour cette recherche")
  await waitWhileLoading()
})
