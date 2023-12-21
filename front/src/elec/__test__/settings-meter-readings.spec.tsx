import { fireEvent, screen } from "@testing-library/react"
import { setEntity, waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { TestRoot, render } from "setupTests"

import { cpo } from "carbure/__test__/data"
import ElecChargingPointsSettings from "elec/components/charging-points/settings"
import server from "../../settings/__test__/api"
import userEvent from "@testing-library/user-event"
import { okChargingPointsApplicationsEmpty, okChargingPointsCheckError, okMeterReadingsApplicationsEmpty, okMeterReadingsCheckError } from "./api"
import ElecMeterReadingsSettings from "elec/components/meter-readings/settings"

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

const getCurrentQuarterString = () => {
  const currentDate = new Date()
  const currentQuarter = currentDate.getMonth() < 3 ? 1 : currentDate.getMonth() < 6 ? 2 : currentDate.getMonth() < 9 ? 3 : 4
  const currentYear = currentDate.getFullYear()
  return "T" + currentQuarter + " " + currentYear

}

// test("check the metter-readings section of the settings", async () => {
//   render(<SettingsWithHooks />)
//   await waitWhileLoading()
//   screen.getByText("Relevés trimestriels")
//   screen.getByText("Transmettre mes relevés trimestriels " + getCurrentQuarterString())
// })


// test("check the applications list", async () => {
//   render(<SettingsWithHooks />)
//   await waitWhileLoading()

//   screen.getByText("Statut")
//   screen.getByText("En attente")
//   screen.getByText("Accepté")
//   screen.getByText("Refusé")


//   screen.getByText("Période")
//   screen.getByText("Stations")
//   screen.getByText("Points de recharge")
//   screen.getByText("Kwh renouvelables")



// })

// test("check the applications list empty", async () => {
//   server.use(okMeterReadingsApplicationsEmpty)
//   setEntity(cpo)

//   render(<SettingsWithHooks />)
//   await waitWhileLoading()
//   screen.getByText("Aucun relevé trimestriel trouvé")
// })

// test("upload dialog opened", async () => {
//   const user = userEvent.setup()
//   setEntity(cpo)

//   render(<SettingsWithHooks />)
//   await waitWhileLoading()

//   const sendButton = await screen.findByText("Transmettre mes relevés trimestriels " + getCurrentQuarterString())
//   await user.click(sendButton)

//   screen.getByText("Relevés trimestriels - " + getCurrentQuarterString())
//   screen.getByText("sur ce lien")
// })

// test("upload file", async () => {
//   const user = userEvent.setup()
//   render(<SettingsWithHooks />)
//   await waitWhileLoading()

//   //Open Upload modal
//   const subscribeButton = await screen.findByText("Inscrire des points de recharge")
//   await user.click(subscribeButton)
//   const uploadButton = await screen.findByText("Vérifier le fichier");
//   expect(uploadButton).toBeDisabled();

//   //Upload file
//   const fileInput = screen.getByLabelText(/Choisir un fichier/i);
//   const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
//   fireEvent.change(fileInput, { target: { files: [file] } });

//   expect(uploadButton).not.toBeDisabled();

//   //Valid upload with success
//   await user.click(uploadButton)
//   await waitWhileLoading()

//   screen.getByText("Inscription des points de recharge")

//   //send inscription
//   const sendButton = await screen.findByText("Envoyer la demande d'inscription")
//   await user.click(sendButton)
//   screen.getByText("Les 90 points de recharge ont été ajoutés !")
// })

test("upload file with error", async () => {
  const user = userEvent.setup()
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()

  //Open Upload modal
  const sendButton = await screen.findByText("Transmettre mes relevés trimestriels " + getCurrentQuarterString())
  await user.click(sendButton)


  //Upload file
  const fileInput = screen.getByLabelText(/Choisir un fichier/i);
  const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
  fireEvent.change(fileInput, { target: { files: [file] } });

  //tester l'ouverture de la modal d'erreur
  const uploadButton = await screen.findByText("Vérifier le fichier");
  server.use(okMeterReadingsCheckError)
  await user.click(uploadButton)
  screen.getByText("À corriger")
})