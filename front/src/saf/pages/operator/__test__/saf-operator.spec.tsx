import { Entity } from "common/types"
import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"

import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { operator } from "common/__test__/data"
import {
  findByTextInNode,
  getField,
  setEntity,
  waitWhileLoading,
} from "common/__test__/helpers"
import { SafOperator } from ".."
import server from "./api"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const SafWithRouter = ({ entity, view }: { entity: Entity; view: string }) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/saf/2021/${view}`}>
      <Route path={`/org/${entity.id}/saf/:year/*`} element={<SafOperator />} />
    </TestRoot>
  )
}

test("display the status tabs", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("11")
  screen.getAllByText("Volumes disponibles")
  screen.getByText("Tickets affectés")
})

test("display ticket sources tab", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  //Filters
  // const header = document.querySelectorAll("main header")[0]
  // if (header) within(header).getAllByText("Clients")
  // let result = screen.getAllByText("Clients").closest("a")
  // expect(result.length).toEqual(2)
  await findByTextInNode("Clients", "INPUT")
  screen.getByText("Matières Premières")
  screen.getByText("Périodes")

  //Status
  screen.getByText("Disponible (11)")
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
  render(<SafWithRouter view="tickets-assigned" entity={operator} />)

  await waitWhileLoading()

  //Filters
  await findByTextInNode("Clients", "INPUT")
  screen.getByText("Matières Premières")
  screen.getByText("Périodes")

  //Status
  screen.getByText("En attente (1)")
  screen.getByText("Refusés (1)")
  screen.getByText("Acceptés (1)")

  //Tableau "En attente"
  let result = screen.getAllByText("En attente")
  expect(result.length).toEqual(2)

  result = screen.getAllByText("Air France")
  expect(result.length).toEqual(2)
})

test("Select a status", async () => {
  render(<SafWithRouter view="tickets-assigned" entity={operator} />)
  const user = userEvent.setup()
  const statusButton = await screen.findByText("Refusés (1)")
  await user.click(statusButton)
  const result = screen.getAllByText("En attente")
  expect(result.length).toEqual(2)
})

test("Select a filter", async () => {
  render(<SafWithRouter view="ticket-sources" entity={operator} />)
  const user = userEvent.setup()
  const filterButton = await findByTextInNode("Clients", "INPUT")
  await user.click(filterButton)

  const filterValue = await screen.findByText("CORSAIR")
  await user.click(filterValue)

  const filterValue2 = await findByTextInNode("Air France", "LABEL")
  await user.click(filterValue2)

  await getField("CORSAIR, Air France")
})
