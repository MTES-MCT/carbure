import { fireEvent, screen } from "@testing-library/react"
import { setEntity, waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { TestRoot, render } from "setupTests"

import userEvent from "@testing-library/user-event"
import { cpo } from "carbure/__test__/data"
import ElecMeterReadingsSettings from "elec/components/meter-readings/settings"
import server from "../../settings/__test__/api"
import { okMeterReadingsApplicationsEmpty, okMeterReadingsApplicationsUrgencyCritical, okMeterReadingsCheckError } from "./api"

const SettingsWithHooks = () => {
  return (
    <TestRoot url={`/org/${cpo.id}/settings`}>
      <Route
        path={`/org/${cpo.id}/settings`}
        element={
          <ElecMeterReadingsSettings companyId={cpo.id} />
        }
      />
    </TestRoot>
  )
}

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" })

})

beforeEach(() => {
  setEntity(cpo)
})
afterEach(() => { server.resetHandlers() })

afterAll(() => server.close())
const openModal = async () => {
  const user = userEvent.setup()
  const sendButton = await screen.findByText("Transmettre mes relevés trimestriels T1 2024")
  return user.click(sendButton)

}

test("check the metter-readings section of the settings", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Relevés trimestriels")
  screen.getByText("Transmettre mes relevés trimestriels T1 2024")
})


const uploadMeterReadingsFile = async () => {
  const user = userEvent.setup()

  const uploadButton = await screen.findByText("Vérifier le fichier");
  expect(uploadButton).toBeDisabled();
  //Upload file
  const fileInput = screen.getByLabelText(/Choisir un fichier/i);
  const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
  fireEvent.change(fileInput, { target: { files: [file] } });
  expect(uploadButton).not.toBeDisabled();

  await user.click(uploadButton)

  return waitWhileLoading()
}


test("check the applications list", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  screen.getByText("Statut")
  screen.getByText("En attente")
  screen.getByText("Accepté")
  screen.getByText("Refusé")


  screen.getByText("Période")
  screen.getByText("Points de recharge")
  screen.getByText("kwh renouvelables")
})



test("check the applications list empty", async () => {
  server.use(okMeterReadingsApplicationsEmpty)
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Aucun relevé trimestriel trouvé")
})

test("upload dialog opened", async () => {
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()

  await openModal()
  screen.getByText("Relevés trimestriels")
  screen.getByText("Relevés trimestriels - T1 2024")
  screen.getByText("Télécharger le fichier Excel")
})

test("upload dialog opened with urgency critical", async () => {
  setEntity(cpo)
  server.use(okMeterReadingsApplicationsUrgencyCritical)
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  await openModal()
  screen.getByText("Le délai de déclaration a été dépassé, l'administration se réserve le droit de la refuser.")
})


test("upload valid file", async () => {
  const user = userEvent.setup()
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  await openModal()
  await uploadMeterReadingsFile()

  //send inscription
  screen.getByText("Valide")
  const validationButton = await screen.findByText("Transmettre mes relevés trimestriels", { selector: "footer button" });
  await user.click(validationButton)
  return waitWhileLoading()

})



test("upload file with error", async () => {
  const user = userEvent.setup()
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()

  await openModal()

  server.use(okMeterReadingsCheckError)
  await uploadMeterReadingsFile()
  screen.getByText("À corriger")
})