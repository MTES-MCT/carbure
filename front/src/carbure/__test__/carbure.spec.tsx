import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { okEmptySettings } from "settings/__test__/api"
import Carbure from "../index"

import server from "./api"
import { MemoryRouter } from "react-router"
import { Suspense } from "react"
import { LoaderOverlay } from "common/components"
import { waitWhileLoading } from "common/__test__/helpers"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => {
  server.resetHandlers()
})
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

  await waitWhileLoading()

  const link = screen.getAllByText("Lier le compte à des sociétés")
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
  screen.getByText("carbure@beta.gouv.fr")
})

test("pick an entity from the menu", async () => {
  render(<CarbureWithRouter />)

  await waitWhileLoading()

  const menu = screen.getByText("Menu")

  userEvent.click(menu)

  const producer = await screen.findByText("Producteur Test")
  userEvent.click(producer)

  screen.getByText("Transactions", { selector: "a" })
  screen.getByText("Société", { selector: "a" })

  userEvent.click(menu)

  const operator = await screen.findByText("Opérateur Test")
  userEvent.click(operator)

  await waitWhileLoading()

  expect(menu.textContent).toBe("Opérateur Test")

  expect(screen.queryByText("Stocks")).toBeNull()
})
