import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { admin, operator, producer, trader } from "common/__test__/data"
import Settings from "../index"
import server, { okDynamicSettings, setEntity } from "./api"

const SettingsWithHooks = ({ entityID }: { entityID?: number }) => {
  return (
    <TestRoot url={`/org/${entityID}/settings`}>
      {(app) => (
        <Route
          path="/org/:entity/settings"
          element={<Settings settings={app.settings} />}
        />
      )}
    </TestRoot>
  )
}

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

beforeEach(() => server.use(okDynamicSettings))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check the company section of the settings for a producer", async () => {
  setEntity(producer)

  render(<SettingsWithHooks entityID={producer.id} />)

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac).toBeChecked()
  expect(trading).toBeChecked()

  userEvent.click(mac)
  userEvent.click(trading)

  await waitFor(() => expect(mac).not.toBeChecked())
  expect(trading).not.toBeChecked()

  userEvent.click(mac)
  userEvent.click(trading)

  await waitFor(() => expect(mac).toBeChecked())
  expect(trading).toBeChecked()
})

test("check the company section of the settings for a trader", async () => {
  setEntity(trader)

  render(<SettingsWithHooks entityID={trader.id} />)

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore

  expect(mac).toBeChecked()

  userEvent.click(mac)

  await waitFor(() => expect(mac).not.toBeChecked())
})

test("check the company section of the settings for an operator", async () => {
  setEntity(operator)

  render(<SettingsWithHooks entityID={operator.id} />)

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore

  expect(mac).toBeChecked()

  userEvent.click(mac)

  await waitFor(() => {
    expect(mac).not.toBeChecked()
  })
})

test("check the company section of the settings for an admin", async () => {
  setEntity(admin)
  render(<SettingsWithHooks entityID={admin.id} />)
  expect(
    screen.queryByText("Options", { selector: ":not(a)" })
  ).not.toBeInTheDocument()
})
