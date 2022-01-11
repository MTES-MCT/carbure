import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"
import { Route } from "react-router-dom"
import { AdminStatus } from "controls/types"

import { waitWhileLoading } from "common/__test__/helpers"
import Controls from "../index"

import server from "./api"

const ControlsWithRouter = ({ status }: { status: AdminStatus }) => (
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
  render(<ControlsWithRouter status="alerts" />)

  await waitWhileLoading()

  await screen.findByText("Alertes")
  screen.getByText("Corrections")
  screen.getByText("Déclarations")

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
