import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { render, TestRoot } from "setupTests"

import ElecSettings from "settings/components/elec"
import server, { okChargingPointsSubscriptionsEmpty } from "./api"
import axios from "axios"

const SettingsWithHooks = () => {
  return (
    <TestRoot url="/org/0/settings">
      <Route
        path="/org/0/settings"
        element={
          <ElecSettings />
        }
      />
    </TestRoot>
  )
}

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" })
})

afterEach(() => { server.resetHandlers() })

afterAll(() => server.close())


test("check the charging point section of the settings", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Inscriptions de points de recharge")
  screen.getByText("Inscrire des points de recharge")
})


test("check the subscriptions list", async () => {
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Statut")
  screen.getByText("Date")
  screen.getByText("31008 kW cumulé")

  screen.getByText("En attente")
  screen.getByText("Accepté")
  screen.getByText("13/11/2023")
  screen.getByText("Refusé")

})

test("check the subscriptions list empty", async () => {
  server.use(okChargingPointsSubscriptionsEmpty)
  render(<SettingsWithHooks />)
  await waitWhileLoading()
  screen.getByText("Aucun point de recharge trouvé")
})

test("upload dialog opened", async () => {
  const user = userEvent.setup()
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

  const subscribeButton = await screen.findByText("Inscrire des points de recharge")
  await user.click(subscribeButton)
  const uploadButton = await screen.findByText("Vérifier le fichier");
  expect(uploadButton).toBeDisabled();

  const fileInput = screen.getByLabelText(/Choisir un fichier/i);
  const file = new File(['(contents)'], 'example.xlsx', { type: 'text/plain' });
  fireEvent.change(fileInput, { target: { files: [file] } });
  expect(uploadButton).not.toBeDisabled();

  //tester l'ouverture de la modal d'erreur
  //tester l'ouverture de la modal valide

})