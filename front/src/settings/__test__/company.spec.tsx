import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { admin, operator, producer, trader } from "carbure/__test__/data"
import Settings from "../index"
import server, {
  okDisableMac,
  okDisableTrading,
  okDynamicSettings,
  okEnableMac,
  okEnableTrading,
} from "./api"
import { setEntity, waitWhileLoading } from "carbure/__test__/helpers"

const SettingsWithHooks = ({ entityID }: { entityID?: number }) => {
  return (
    <TestRoot url={`/org/${entityID}/settings`}>
      <Route path="/org/:entity/settings" element={<Settings />} />
    </TestRoot>
  )
}

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))

beforeEach(() => server.use(okDynamicSettings))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check the company section of the settings for a producer", async () => {
  const user = userEvent.setup()
  setEntity(producer)

  render(<SettingsWithHooks entityID={producer.id} />)

  await waitWhileLoading()

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  await screen.findByDisplayValue("litres (Éthanol à 20°, autres à 15°)")

  const mac = screen.getByLabelText("Ma société effectue des mises à consommation (B100 et ED95 uniquement)") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac).toBeChecked()
  expect(trading).toBeChecked()

  server.use(okDisableMac)
  await user.click(mac)
  // await waitWhileLoading()
  expect(mac).not.toBeChecked()

  server.use(okDisableTrading)
  await user.click(trading)
  // await waitWhileLoading()
  expect(trading).not.toBeChecked()

  server.use(okEnableMac)
  await user.click(mac)
  // await waitWhileLoading()
  expect(mac).toBeChecked()

  server.use(okEnableTrading)
  await user.click(trading)
  // await waitWhileLoading()
  expect(trading).toBeChecked()
})

test("check the company section of the settings for a trader", async () => {
  const user = userEvent.setup()
  setEntity(trader)

  render(<SettingsWithHooks entityID={trader.id} />)

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des mises à consommation (B100 et ED95 uniquement)") // prettier-ignore

  expect(mac).toBeChecked()

  server.use(okDisableMac)
  await user.click(mac)
  await waitFor(() => expect(mac).not.toBeChecked())
})

test("check the company section of the settings for an operator", async () => {
  const user = userEvent.setup()
  setEntity(operator)

  render(<SettingsWithHooks entityID={operator.id} />)

  expect(await screen.findAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des mises à consommation (B100 et ED95 uniquement)") // prettier-ignore

  expect(mac).toBeChecked()

  server.use(okDisableMac)
  await user.click(mac)
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
