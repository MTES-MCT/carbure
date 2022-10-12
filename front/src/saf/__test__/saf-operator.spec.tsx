import { Entity } from "carbure/types"
import { Route } from "react-router-dom"
import { setEntity } from "settings/__test__/api"
import { TestRoot } from "setupTests"

import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { operator } from "carbure/__test__/data"
import { getField, waitWhileLoading } from "carbure/__test__/helpers"
import { Saf } from "../index"
import server from "./api"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const SafWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: string
}) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/saf/2021/${status}`}>
      <Route path={`/org/${entity.id}/saf/:year/*`} element={<Saf />} />
    </TestRoot>
  )
}

test("display the status tabs", async () => {
  render(<SafWithRouter status="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("15 000")
  screen.getByText("Litres à affecter")
  screen.getByText("Tickets envoyés")

  //Filters
  screen.getByText("Clients")
  screen.getByText("Matières Premières")
  screen.getByText("Périodes")

  //Status
  screen.getByText("Disponible (2)")
  screen.getByText("Historique (3)")

  //Pagination
  screen.getByText("résultats")
})

test("Select a filter", async () => {
  render(<SafWithRouter status="ticket-sources" entity={operator} />)
  const user = userEvent.setup()
  const filter = await screen.findByText("Clients")
  await user.click(filter)
  const filterValue = await screen.findByText("CORSAIR")
  await user.click(filterValue)
  const filterValue2 = await screen.findByText("Air France")
  await user.click(filterValue2)
  getField("CORSAIR, Air France")
})
