import { render, TestRoot } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from 'react-router-dom'

import { admin, operator, producer, trader } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import Settings from "../index"
import server, { okDynamicSettings, setEntity } from "./api"

const SettingsWithHooks = () => {
  return (
    <TestRoot url="/org/0/settings">
      {(app) => (
        <Route path="/org/0/settings" element={
          <Settings 
            entity={app.settings.data?.rights[0].entity ?? null}
            settings={app.settings}
          />
        } />
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

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  expect(screen.getAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac).toBeChecked()
  expect(trading).toBeChecked()

  userEvent.click(mac)
  userEvent.click(trading)

  await waitWhileLoading()

  await waitFor(() => expect(mac).not.toBeChecked())
  expect(trading).not.toBeChecked()

  userEvent.click(mac)
  userEvent.click(trading)

  await waitWhileLoading()

  await waitFor(() => expect(mac).toBeChecked())
  expect(trading).toBeChecked()
})

test("check the company section of the settings for a trader", async () => {
  setEntity(trader)

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  expect(screen.getAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore

  expect(mac).toBeChecked()

  userEvent.click(mac)

  await waitWhileLoading()
  await waitFor(() => expect(mac).not.toBeChecked())
})

test("check the company section of the settings for an operator", async () => {
  setEntity(operator)

  render(<SettingsWithHooks />)

  await waitWhileLoading()

  expect(screen.getAllByText("Options")).toHaveLength(2)

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore

  expect(mac).toBeChecked()

  userEvent.click(mac)

  await waitWhileLoading()

  await waitFor(() => {
    expect(mac).not.toBeChecked()
  })
})

test("check the company section of the settings for an admin", async () => {
  setEntity(admin)
  render(<SettingsWithHooks />)
  expect(
    screen.queryByText("Options", { selector: ":not(a)" })
  ).not.toBeInTheDocument()
})
