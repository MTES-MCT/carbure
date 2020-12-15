import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from "common/types"
import {
  isccCertificate,
  expiredISCCCertificate,
  producer,
} from "common/__test__/data"
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

  screen.getByText("Certificats ISCC")
  screen.getByText("Ajouter un certificat ISCC")
  screen.getByText("Aucun certificat ISCC trouvé")
})

test("add an iscc certificate in settings", async () => {
  render(<SettingsWithHooks entity={producer} />)

  userEvent.click(screen.getByText("Ajouter un certificat ISCC"))

  // wait for dialog to open
  const input = screen.getByLabelText("Certificat ISCC")

  userEvent.type(input, "Test")

  const option = await waitFor(() =>
    screen.getByText("ISCC Test - Holder Test")
  )

  userEvent.click(option)

  await waitFor(() => {
    expect(input.getAttribute("value")).toBe("ISCC Test - Holder Test")
  })

  userEvent.click(screen.getByText("Ajouter"))

  await waitFor(() => {
    screen.getByText("ISCC Test")
    screen.getByText("Holder Test")
    screen.getByText("Scope Test")
    screen.getByText("24/04/2021")
  })
})

test("delete an iscc certificate in settings", async () => {
  setISCCCertificates([isccCertificate])

  render(<SettingsWithHooks entity={producer} />)

  const deleteButton = await waitFor(() => {
    screen.getByText("ISCC Test")
    screen.getByText("Holder Test")
    screen.getByText("Scope Test")

    return screen.getByTitle("Supprimer le certificat").closest("svg")!
  })

  // click on the delete button and then confirm the action on the popup
  userEvent.click(deleteButton)
  screen.getByText("Suppression certificat")
  userEvent.click(screen.getByText("OK"))

  await waitFor(() => {
    screen.getByText("Aucun certificat ISCC trouvé")
  })
})

test("renew a certificate", async () => {
  setISCCCertificates([expiredISCCCertificate])

  render(<SettingsWithHooks entity={producer} />)

  const updateButton = await waitFor(() => {
    screen.getByText("Expired ISCC Test")
    screen.getByText("Expired Holder Test")
    screen.getByText("Expired Scope Test")
    screen.getByText("Expiré (01/01/2000)")

    return screen.getByText("Mise à jour")
  })

  userEvent.click(updateButton)
  screen.getByText("Mise à jour certificat ISCC")

  userEvent.type(screen.getByLabelText("Certificat ISCC"), "Test")
  const option = await waitFor(() => screen.getByText("ISCC Test - Holder Test")) // prettier-ignore
  userEvent.click(option)

  userEvent.click(screen.getByText("Ajouter"))

  await waitFor(() => {
    screen.getByText("ISCC Test")
  })
})
