import { Suspense } from "react"
import { MemoryRouter } from "react-router"
import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Carbure from "../index"
import server from "./api"
import { LoaderOverlay } from "common/components/scaffold"
import { okEmptySettings, okSettings } from "settings/__test__/api"
import {
  okLots,
  okSnapshot,
  okYears,
  okSummary,
} from "transactions/__test__/api"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
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
  const user = userEvent.setup()

  server.use(okEmptySettings)
  render(<CarbureWithRouter />)

  const link = await screen.findAllByText("Lier le compte à des sociétés")
  await user.click(link[0].closest("a")!)

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
  const user = userEvent.setup()

  server.use(okSettings, okSnapshot, okYears, okLots, okSummary)
  render(<CarbureWithRouter />)

  const menu = await screen.findByText("Menu")

  await user.click(menu)

  const producer = await screen.findByText("Producteur Test")
  await user.click(producer)

  screen.getByText("Transactions", { selector: "a" })
  screen.getByText("Société", { selector: "a" })

  await user.click(menu)

  const operator = await screen.findAllByText("Opérateur Test")
  await user.click(operator[1])

  expect(menu.textContent).toBe("Opérateur Test")
})
