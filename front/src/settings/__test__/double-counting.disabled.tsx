import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "react-router-dom"
import { render, TestRoot } from "setupTests"

import { producer } from "carbure/__test__/data"
import {
  getField,
  uploadFileField,
  waitWhileLoading,
} from "carbure/__test__/helpers"
import DoubleCountingSettings from "settings/components/double-counting"
import server, {
  koDoubleCountUploadApplication,
  okDoubleCountUploadApplication,
  okDynamicSettings,
  setEntity,
} from "./api"

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

beforeAll(() =>
  server.listen({
    onUnhandledRequest: "warn",
  })
)

beforeEach(() => server.use(okDynamicSettings))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("check double counting upload ", async () => {
  server.use(okDoubleCountUploadApplication)
  const user = userEvent.setup()
  setEntity(producer)
  render(<SettingsWithHooks entityID={producer.id} />)
  await fillForm()
})

test.skip("check double counting upload with error display errors", async () => {
  server.use(koDoubleCountUploadApplication)
  const user = userEvent.setup()
  setEntity(producer)
  render(<SettingsWithHooks entityID={producer.id} />)

  await fillForm()

  await waitWhileLoading()

  await screen.getByText(
    "Approvisionnement - Ligne 2 : La matière première FUIMERAav n'est pas reconnue. Vérifiez la syntaxe de ce code."
  )

  //UNKNOWN_BIOFUEL
  await screen.getByText(
    "Production - Ligne 2 : Le biocarburant SFALKWJ n'est pas reconnu. Vérifiez la syntaxe de ce code."
  )

  //UNKNOWN_FEEDSTOCK
  await screen.getByText(
    "Production - Ligne 3 : La matière première Asdasasfw2323 n'est pas reconnue. Vérifiez la syntaxe de ce code."
  )

  //MISSING_BIOFUEL
  await screen.getByText("Production - Ligne 4 : Le biocarburant est manquant.")

  //NOT_DC_FEEDSTOCK
  await screen.getByText(
    "Production - Ligne 5 : La matière première Blé n'est pas comprise dans la liste des matières premières pouvant être double comptées."
  )

  //MP_BC_INCOHERENT
  await screen.getByText(
    "Production - Ligne 4 : La matière première Marc de raisin est incohérente avec le biocarburant B100."
  )
  //PRODUCTION_MISMATCH_SOURCING
  await screen.getByText(
    "En 2002, la quantité de matière première approvisionnée (8000 tonnes de Marc de raisin) doit être supérieure à la quantité de biocarburant produite estimée (10000 tonnes)."
  )

  //POME_GT_2000
  await screen.getByText(
    "Production - La production estimée de biocarburant à partir d'Effluents d'huileries de palme et rafles ne doit pas excéder 2000 tonnes par an pour une usine de production."
  )

  //Not unrecognized errors
  try {
    await screen.getByText("Erreur de validation")
  } catch (error) {
    expect(error).not.toBeNull()
  }
})

const fillForm = async () => {
  const user = userEvent.setup()

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
}
