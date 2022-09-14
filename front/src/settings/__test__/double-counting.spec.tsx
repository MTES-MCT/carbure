import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { admin, operator, producer, trader } from "carbure/__test__/data"
import Settings from "../index"
import server, { okDynamicSettings, setEntity } from "./api"
import { waitWhileLoading } from "carbure/__test__/helpers"
import DoubleCountingSettings from "settings/components/double-counting"

const SettingsWithHooks = ({ entityID }: { entityID?: number }) => {
  return (
    <TestRoot url={`/org/${entityID}/settings`}>
      <Route
        path="/org/:entity/settings"
        element={<DoubleCountingSettings />}
      />
    </TestRoot>
  )
}

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

beforeEach(() => server.use(okDynamicSettings))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check upload a double counting application", async () => {
  const user = userEvent.setup()
  setEntity(producer)
  render(<SettingsWithHooks entityID={producer.id} />)
  await waitWhileLoading()
  await screen.getByText("Dossiers double comptage")
})
