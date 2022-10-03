import { Entity } from "carbure/types"
import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"
import { setEntity } from "settings/__test__/api"

import Transactions, { SafCertificates } from "../index"
import { render, screen } from "@testing-library/react"
import { Data, waitWhileLoading } from "carbure/__test__/helpers"
import { operator } from "carbure/__test__/data"
import server from "./api"
import { safSnapshot, safCertificates } from "./data"
import userEvent from "@testing-library/user-event"
import Flags from "flags.json"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
// beforeEach(() => {
//   // Data.set("saf-snapshot", safSnapshot)
//   // Data.set("saf-certificates", safCertificates)
// })
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const SafCertificatesWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: string
}) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/saf-certificates/2021/${status}`}>
      <Route
        path={`/org/${entity.id}/saf-certificates/:year/*`}
        element={<SafCertificates />}
      />
    </TestRoot>
  )
}

test("display an empty list of transactions", async () => {
  render(<SafCertificatesWithRouter status="to-assign" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("4")
  screen.getByText("Lots SAF")
  screen.getByText("Certificats en attente")
  screen.getByText("Certificats refusés")
  screen.getByText("Certificats acceptés")
})
