import { fireEvent, screen } from "@testing-library/react"
import { setEntity, waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { TestRoot, render } from "setupTests"

import { cpo } from "carbure/__test__/data"
import ElecChargePointsSettings from "elec/components/charge-points/settings"
import server from "../../settings/__test__/server"
import userEvent from "@testing-library/user-event"
import {
  okChargePointsApplicationsEmpty,
  okChargePointsCheckError,
} from "./api"

const SettingsWithHooks = () => {
  return (
    <TestRoot url={`/org/${cpo.id}/settings`}>
      <Route
        path={`/org/${cpo.id}/settings`}
        element={<ElecChargePointsSettings companyId={cpo.id} />}
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
afterEach(() => {
  server.resetHandlers()
})

afterAll(() => server.close())

test("check the charge point section of the settings", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Inscriptions de points de recharge")
  screen.getByText("Inscrire des points de recharge")
})

test("check the applications list", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Statut")
  screen.getByText("Date d'ajout")
  screen.getByText("30 000")

  screen.getByText("En attente")
  screen.getByText("Accepté")
  screen.getByText("13/11/2023")
  screen.getByText("Refusé")
})

test("check the applications list empty", async () => {
  server.use(okChargePointsApplicationsEmpty)
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

  const subscribeButton = await screen.findByText(
    "Inscrire des points de recharge"
  )
  await user.click(subscribeButton)

  screen.getByText(
    "Cet outil vous permet de vérifier la conformité de votre demande d'inscription."
  )
  const templateButton = screen.getByText("sur ce lien")
  user.click(templateButton)

  const url = templateButton.getAttribute("href")
  expect(url).toEqual("/templates/points-de-recharge-inscription.xlsx")
})

const uploadChargePointsFile = async () => {
  const user = userEvent.setup()

  //Open Upload modal
  const subscribeButton = await screen.findByText(
    "Inscrire des points de recharge"
  )
  await user.click(subscribeButton)
  const uploadButton = await screen.findByText("Vérifier le fichier")
  expect(uploadButton).toBeDisabled()

  //Upload file
  const fileInput = screen.getByLabelText(/Choisir un fichier/i)
  const file = new File(["(contents)"], "example.xlsx", { type: "text/plain" })
  fireEvent.change(fileInput, { target: { files: [file] } })
  expect(uploadButton).not.toBeDisabled()

  await user.click(uploadButton)

  return waitWhileLoading()
}

test("upload file", async () => {
  const user = userEvent.setup()
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  await uploadChargePointsFile()
  screen.getByText("Valide")

  //send inscription
  const sendButton = await screen.findByText("Envoyer la demande d'inscription")
  await user.click(sendButton)
  screen.getByText(
    "La demande d'inscription des 90 points de recharge a été ajoutée !"
  )
})

test("upload file with error", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()

  //tester l'ouverture de la modal d'erreur
  server.use(okChargePointsCheckError)
  await uploadChargePointsFile()
  screen.getByText("À corriger")
})
