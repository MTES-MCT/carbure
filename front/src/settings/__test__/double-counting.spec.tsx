import { render, TestRoot } from "setupTests"
import { waitFor, screen, fireEvent } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"

import { admin, operator, producer, trader } from "carbure/__test__/data"
import Settings from "../index"
import server, { okDynamicSettings, setEntity } from "./api"
import {
  getField,
  uploadFileField,
  waitWhileLoading,
} from "carbure/__test__/helpers"
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
  await screen.getByText("Dossiers double comptage")

  const button = await screen.findByText("Ajouter un dossier double comptage")
  await user.click(button)

  const depotInput = await getField("Site de production")
  await user.type(depotInput, "Test")
  await user.click(await screen.findByText("Test Production Site"))
  await screen.findByDisplayValue("Test Production Site")

  const dcInput = await uploadFileField(
    "Importer les informations double comptage"
  )
  expect(dcInput.files).toHaveLength(1)

  const descriptionInput = await uploadFileField("Importer la description")
  expect(descriptionInput.files).toHaveLength(1)

  const submitButton = await screen.findByText("Soumettre le dossier")
  await user.click(submitButton)
})
