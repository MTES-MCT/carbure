import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { okEmptySettings, setEntity } from "settings/__test__/api"
import Carbure from "../index"

import server from "./api"
import { MemoryRouter } from "react-router"
import { Suspense } from "react"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { producer } from "common-v2/__test__/data"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
beforeEach(() => setEntity(producer))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const CarbureWithRouter = () => {
  return (
    <MemoryRouter>
      <Suspense fallback={<LoaderOverlay />}>
        <Carbure />
      </Suspense>
    </MemoryRouter>
  )
}

test("display alert message when connected without access rights", async () => {
  server.use(okEmptySettings)
  render(<CarbureWithRouter />)

  const link = await screen.findAllByText("Lier le compte à des sociétés")
  userEvent.click(link[0].closest("a")!)

  await screen.findByText("🌻 Bienvenue sur CarbuRe")

  screen.getByText("Menu")

  screen.getByText("Il semblerait que votre compte ne soit lié à aucune entité enregistrée sur CarbuRe.") // prettier-ignore

  screen.getByText("Veuillez vous rendre sur la page du menu pour effectuer une demande d'accès.") // prettier-ignore
  screen.getByText("Mon Compte")

  screen.getByText("Vous avez des questions concernant le fonctionnement de CarbuRe ?") // prettier-ignore

  screen.getByText("Notre FAQ")
  screen.getByText('contient de nombreuses ressources pouvant vous aider dans votre utilisation du produit.') // prettier-ignore

  // screen.getByText("Pour plus d'informations contactez nous sur ou par e-mail à l'addresse.") // prettier-ignore
  screen.getByText("le Slack de CarbuRe")
  screen.getByText("disponible sur ce lien")
})

test("pick an entity from the menu", async () => {
  render(<CarbureWithRouter />)

  const menu = await screen.findByText("Menu")

  userEvent.click(menu)

  const producer = await screen.findByText("Producteur Test")
  userEvent.click(producer)

  screen.getByText("Transactions", { selector: "a" })
  screen.getByText("Société", { selector: "a" })

  userEvent.click(menu)

  const operator = await screen.findByText("Opérateur Test")
  userEvent.click(operator)

  expect(menu.textContent).toBe("Opérateur Test")

  await screen.findAllByTestId("loader")
})
