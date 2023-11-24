import { fireEvent, screen } from "@testing-library/react"
import { waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { TestRoot, render } from "setupTests"

import { cpo } from "carbure/__test__/data"
import ElecSettings from "settings/components/charging-points"
import server, { okChargingPointsCheckError, okChargingPointsApplicationsEmpty, setEntity } from "./api"
import userEvent from "@testing-library/user-event"

const SettingsWithHooks = () => {
  return (
    <TestRoot url={`/org/${cpo.id}/settings`}>
      <Route
        path={`/org/${cpo.id}/settings`}
        element={
          <ElecSettings companyId={cpo.id} />
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


test("check the charging point section of the settings", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Inscriptions de points de recharge")
  screen.getByText("Inscrire des points de recharge")
})


test("check the applications list", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Statut")
  screen.getByText("Date")
  screen.getByText("31008")

  screen.getByText("En attente")
  screen.getByText("Accepté")
  screen.getByText("13/11/2023")
  screen.getByText("Refusé")

})

test("check the applications list empty", async () => {
  server.use(okChargingPointsApplicationsEmpty)
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Aucun point de recharge trouvé")
})

test("upload dialog opened", async () => {
  const user = userEvent.setup()
  setEntity(cpo)

  render(<SettingsWithHooks />)
  await waitWhileLoading()

  const subscribeButton = await screen.findByText("Inscrire des points de recharge")
  await user.click(subscribeButton)

  screen.getByText("Cet outil vous permet de vérifier la conformité de votre demande d’inscription.")
  const templateButton = screen.getByText("sur ce lien")
  user.click(templateButton)

  const url = templateButton.getAttribute('href')
  expect(url).toEqual("/templates/points-de-recharge-inscription.xlsx")

})

test("upload file", async () => {
  const user = userEvent.setup()
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  //Open Upload modal
  const subscribeButton = await screen.findByText("Inscrire des points de recharge")
  await user.click(subscribeButton)
  const uploadButton = await screen.findByText("Vérifier le fichier");
  expect(uploadButton).toBeDisabled();

  //Upload file
  const fileInput = screen.getByLabelText(/Choisir un fichier/i);
  const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
  fireEvent.change(fileInput, { target: { files: [file] } });

  expect(uploadButton).not.toBeDisabled();

  //Valid upload with success
  await user.click(uploadButton)
  await waitWhileLoading()

  screen.getByText("Inscription des points de recharge")

  //send inscription
  const sendButton = await screen.findByText("Envoyer la demande d'inscription")
  await user.click(sendButton)
  screen.getByText("Les 90 points de recharge ont été ajoutés !")

})

test("upload file with error", async () => {
  const user = userEvent.setup()
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  //Open Upload modal
  const subscribeButton = await screen.findByText("Inscrire des points de recharge")
  await user.click(subscribeButton)
  const uploadButton = await screen.findByText("Vérifier le fichier");

  //Upload file
  const fileInput = screen.getByLabelText(/Choisir un fichier/i);
  const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
  fireEvent.change(fileInput, { target: { files: [file] } });

  //tester l'ouverture de la modal d'erreur
  server.use(okChargingPointsCheckError)
  await user.click(uploadButton)
  screen.getByText("Correction du dossier double comptage")

})