import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import {
  isccCertificate,
  expiredISCCCertificate,
  producer,
} from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"

import server, { setISCCCertificates } from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  setISCCCertificates([])
})

afterAll(() => server.close())

test("check the iscc certificate section of the settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  expect(screen.getAllByText("Certificats ISCC")).toHaveLength(2)
  screen.getByText("Ajouter un certificat ISCC")
  screen.getByText("Aucun certificat ISCC trouvé")
})

test("add an iscc certificate in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  userEvent.click(screen.getByText("Ajouter un certificat ISCC"))

  // wait for dialog to open
  const input = await screen.findByLabelText("Certificat ISCC")
  userEvent.type(input, "Test")

  const option = await screen.findByText("ISCC Test - Holder Test")
  userEvent.click(option)

  userEvent.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("ISCC Test")
  screen.getByText("Holder Test")
  screen.getByText("Scope Test")
  screen.getByText("24/04/2021")
})

test("delete an iscc certificate in settings", async () => {
  setISCCCertificates([isccCertificate])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  const deleteButton = await screen.findByTitle("Supprimer le certificat")
  screen.getByText("ISCC Test")
  screen.getByText("Holder Test")
  screen.getByText("Scope Test")

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)

  screen.getByText("Suppression certificat")
  userEvent.click(screen.getByText("OK"))

  await waitWhileLoading()

  await screen.findByText("Aucun certificat ISCC trouvé")
})

test("renew a certificate", async () => {
  setISCCCertificates([expiredISCCCertificate])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  const updateButton = await screen.findByText("Mise à jour")
  screen.getByText("Expired ISCC Test")
  screen.getByText("Expired Holder Test")
  screen.getByText("Expired Scope Test")
  screen.getByText("Expiré (01/01/2000)")

  userEvent.click(updateButton)
  screen.getByText("Mise à jour certificat ISCC")

  userEvent.type(screen.getByLabelText("Certificat ISCC"), "Test")
  const option = await screen.findByText("ISCC Test - Holder Test")
  userEvent.click(option)

  userEvent.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("ISCC Test")
})
