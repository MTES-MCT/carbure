import { fireEvent, screen } from "@testing-library/react"
import { setEntity, waitWhileLoading } from "carbure/__test__/helpers"
import { Route } from "react-router-dom"
import { TestRoot, render } from "setupTests"

import { admin } from "carbure/__test__/data"
import ElecAdminAudit from "elec-audit-admin"
import { setupServer } from "msw/node"
import {
  okGenerateSample,
  okGetChargePointsApplicationDetails,
  okGetChargePointsApplications,
  okGetSnapshot,
  okGetYears,
  okStartChargePointsApplicationAudit,
} from "./api"
import { okSettings } from "account/__test__/api"
import userEvent from "@testing-library/user-event"

const server = setupServer(
  okSettings,
  okGetYears,
  okGetSnapshot,
  okGetChargePointsApplications
)

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" })
})
afterEach(() => {
  server.resetHandlers()
})
afterAll(() => server.close())

const ChargePointsApplications = () => {
  setEntity(admin)

  return (
    <TestRoot url={`/org/${admin.id}/elec-admin-audit/2024/charge-points`}>
      <Route
        path={`/org/:entity/elec-admin-audit/:year/charge-points/*`}
        element={<ElecAdminAudit />}
      />
    </TestRoot>
  )
}

test("check the charge points applications listing", async () => {
  render(<ChargePointsApplications />)
  await waitWhileLoading()
  screen.getByText("Audit des points de recharge")
  screen.getByText("En attente (1)")
  screen.getByText("En attente")
  screen.getByText("Refusé")
  screen.getByText("En cours d'audit")
  screen.getByText("Audit réalisé")
  screen.getByText("Accepté")
})

test("check the sample generation", async () => {
  render(<ChargePointsApplications />)
  await waitWhileLoading()

  const user = userEvent.setup()
  const PendingApplicationItem = await screen.findByText("En attente")

  server.use(okGetChargePointsApplicationDetails)
  await user.click(PendingApplicationItem)
  await waitWhileLoading()

  screen.getByText("Inscription de points de recharge")
  screen.getByText("Génération de l'échantillon à auditer")

  // const percentageInput = screen.getByLabelText("Pourcentage de puissance installée à auditeur (%)")
  const generateButton = await screen.findByText("Générer l'échantillon")
  server.use(okGenerateSample)
  await user.click(generateButton)
  screen.getByText("Pourcentage de puissance installée à auditeur")

  const downloadButton = await screen.findByText("Télécharger l'échantillon")
  await user.click(downloadButton)
  screen.getByText("Génération de l'email")

  const generateEmailButton = await screen.findByText("Générer l'email")
  await user.click(generateEmailButton)
  screen.getByText("Confirmation de l'envoie de l'ordre de contrôle")

  const sendButton = await screen.findByText("Envoyer en audit")
  expect(sendButton).toBeDisabled()

  const confirmCheckbox = await screen.getByLabelText(
    "Je confirme avoir envoyé l'ordre de contrôle par e-mail avec l'échantillon en pièce jointe."
  )
  await user.click(confirmCheckbox)
  expect(sendButton).toBeEnabled()

  server.use(okStartChargePointsApplicationAudit)
  await user.click(sendButton)
  screen.getByText(
    "L'audit de l'échantillon des 2 points de recharge a bien été initié."
  )
})
