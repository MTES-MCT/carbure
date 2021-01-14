import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import {
  dbsCertificate,
  expired2BSCertificate,
  producer,
} from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { useGetSettings } from "settings/hooks/use-get-settings"
import Settings from "../index"

import server, { set2BSCertificates } from "./api"

const SettingsWithHooks = ({ entity }: { entity: Entity }) => {
  const settings = useGetSettings()
  return <Settings entity={entity} settings={settings} />
}

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  set2BSCertificates([])
})

afterAll(() => server.close())

test("check the 2bs certificate section of the settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  screen.getByText("Certificats 2BS")
  screen.getByText("Ajouter un certificat 2BS")
  screen.getByText("Aucun certificat 2BS trouvé")
})

test("add a 2bs certificate in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  userEvent.click(screen.getByText("Ajouter un certificat 2BS"))

  // wait for dialog to open
  const input = screen.getByLabelText("Certificat 2BS")

  userEvent.type(input, "Test")

  const option = await screen.findByText("2BS Test - Holder Test")

  userEvent.click(option)

  await waitFor(() => {
    expect(input.getAttribute("value")).toBe("2BS Test - Holder Test")
  })

  userEvent.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("2BS Test")
  screen.getByText("Holder Test")
  screen.getByText("Scope Test")
  screen.getByText("24/04/2021")
})

test("delete a 2bs certificate in settings", async () => {
  set2BSCertificates([dbsCertificate])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  const deleteButton = screen.getByTitle("Supprimer le certificat")

  screen.getByText("2BS Test")
  screen.getByText("Holder Test")
  screen.getByText("Scope Test")

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  screen.getByText("Suppression certificat")
  userEvent.click(screen.getByText("OK"))

  await waitWhileLoading()

  await screen.findByText("Aucun certificat 2BS trouvé")
})

test("renew a certificate", async () => {
  set2BSCertificates([expired2BSCertificate])

  render(<SettingsWithHooks entity={producer} />)

  await waitWhileLoading()

  screen.getByText("Expired 2BS Test")
  screen.getByText("Expired Holder Test")
  screen.getByText("Expired Scope Test")
  screen.getByText("Expiré (01/01/2000)")

  const updateButton = screen.getByText("Mise à jour")

  userEvent.click(updateButton)
  screen.getByText("Mise à jour certificat 2BS")

  userEvent.type(screen.getByLabelText("Certificat 2BS"), "Test")
  const option = await screen.findByText("2BS Test - Holder Test")
  userEvent.click(option)

  userEvent.click(screen.getByText("Ajouter"))

  await waitWhileLoading()

  await screen.findByText("2BS Test")
  expect(screen.queryByText("Expired 2BS Test")).not.toBeInTheDocument()
})
