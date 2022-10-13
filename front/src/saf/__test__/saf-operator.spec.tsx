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

const SafWithRouter = ({ entity, view }: { entity: Entity; view: string }) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/saf/2021/${view}`}>
      <Route path={`/org/${entity.id}/saf/:year/*`} element={<Saf />} />
    </TestRoot>
  )
}

test("display the status tabs", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("15 000")
  screen.getByText("Litres à affecter")
  screen.getByText("Tickets envoyés")
})

test("display ticket sources tab", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  //Filters
  screen.getByText("Clients")
  screen.getByText("Matières Premières")
  screen.getByText("Périodes")

  //Status
  screen.getByText("Disponible (2)")
  screen.getByText("Historique (3)")

  //Tableau
  let result = screen.getAllByText("Disponible")
  expect(result.length).toEqual(11)

  result = screen.getAllByText("3 000 L")
  expect(result.length).toEqual(3)
  result = screen.getAllByText("/10 000 L")
  expect(result.length).toEqual(8)

  //Pagination
  screen.getByText("résultats")
})

test("display tickets tab", async () => {
  render(<SafWithRouter view="tickets" entity={operator} />)

  await waitWhileLoading()

  //Filters
  screen.getByText("Clients")
  screen.getByText("Matières Premières")
  screen.getByText("Périodes")

  //Status
  screen.getByText("En attente (2)")
  screen.getByText("Refusés (1)")
  screen.getByText("Acceptés (1)")

  //Tableau "En attente"
  let result = screen.getAllByText("En attente")
  expect(result.length).toEqual(2)

  result = screen.getAllByText("Air France")
  expect(result.length).toEqual(2)
})

test("Select a status", async () => {
  render(<SafWithRouter view="tickets" entity={operator} />)
  const user = userEvent.setup()
  const statusButton = await screen.findByText("Refusés (1)")
  await user.click(statusButton)
  let result = screen.getAllByText("Refusé")
  expect(result.length).toEqual(2)
})

test("Select a filter", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)
  const user = userEvent.setup()
  const filter = await screen.findByText("Clients")
  await user.click(filter)
  const filterValue = await screen.findByText("CORSAIR")
  await user.click(filterValue)
  const filterValue2 = await screen.findByText("Air France")
  await user.click(filterValue2)
  getField("CORSAIR, Air France")
})
