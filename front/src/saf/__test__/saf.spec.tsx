import { Entity } from "carbure/types"
import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"
import { setEntity } from "settings/__test__/api"

import Transactions, { Saf } from "../index"
import { render, screen } from "@testing-library/react"
import { Data, waitWhileLoading } from "carbure/__test__/helpers"
import { operator } from "carbure/__test__/data"
import server from "./api"
import { safOperatorSnapshot, safTicketSources } from "./data"
import userEvent from "@testing-library/user-event"
import Flags from "flags.json"

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
      <Route
        path={`/org/${entity.id}/saf/:year/*`}
        element={<Saf />}
      />
    </TestRoot>
  )
}

test("display an empty list of transactions", async () => {
  render(<SafWithRouter status="ticket-sources" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("4")
  screen.getByText("Lots SAF")
  screen.getByText("Certificats en attente")
  screen.getByText("Certificats refusés")
  screen.getByText("Certificats acceptés")
})
