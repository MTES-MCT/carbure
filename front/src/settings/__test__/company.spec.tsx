import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import { admin, operator, producer, trader } from "common/__test__/data"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"
import server from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check the company section of the settings for a producer", async () => {
  render(<SettingsWithHooks entity={producer} />)

  screen.getByText("Options")

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac.hasAttribute("checked")).toBe(true)
  expect(trading.hasAttribute("checked")).toBe(true)

  userEvent.click(mac)
  userEvent.click(trading)

  waitFor(() => {
    expect(mac.hasAttribute("checked")).toBe(false)
    expect(trading.hasAttribute("checked")).toBe(false)
  })
})

test("check the company section of the settings for a trader", async () => {
  render(<SettingsWithHooks entity={trader} />)

  screen.getByText("Options")

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac.hasAttribute("checked")).toBe(true)
  expect(trading.hasAttribute("checked")).toBe(true)
  expect(trading.hasAttribute("disabled")).toBe(true)

  userEvent.click(mac)

  waitFor(() => {
    expect(mac.hasAttribute("checked")).toBe(false)
  })
})

test("check the company section of the settings for an operator", async () => {
  render(<SettingsWithHooks entity={operator} />)

  screen.getByText("Options")

  const mac = screen.getByLabelText("Ma société effectue des Mises à Consommation") // prettier-ignore
  const trading = screen.getByLabelText("Ma société a une activité de négoce")

  expect(mac.hasAttribute("checked")).toBe(true)
  expect(trading.hasAttribute("checked")).toBe(false)
  expect(trading.hasAttribute("disabled")).toBe(true)

  userEvent.click(mac)

  waitFor(() => {
    expect(mac.hasAttribute("checked")).toBe(false)
  })
})

test("check the company section of the settings for an admin", async () => {
  render(<SettingsWithHooks entity={admin} />)
  expect(screen.queryByText("Options")).toBeNull()
})
