import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { okEmptySettings } from "settings/__test__/api"
import Carbure from "../index"

import server from "./api"

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
})
afterAll(() => server.close())

const CarbureWithRouter = () => {
  return (
    <MemoryRouter>
      <Carbure />
    </MemoryRouter>
  )
}

test("display alert message when connected without access rights", async () => {
  server.use(okEmptySettings)

  render(<CarbureWithRouter />)

  await screen.findByText("🌻 Bienvenue sur CarbuRe")

  screen.getByText("Menu")

  screen.getByText("Il semblerait que votre compte ne soit lié à aucune entité enregistrée sur CarbuRe.") // prettier-ignore

  screen.getByText("Veuillez vous rendre sur la pagedu menu pour effectuer une demande d'accès.") // prettier-ignore
  screen.getByText("Mon Compte")

  screen.getByText("Vous avez des questions concernant le fonctionnement de CarbuRe ?") // prettier-ignore

  screen.getByText("Notre FAQ")
  screen.getByText('contient de nombreuses ressources pouvant vous aider dans votre utilisation du produit.') // prettier-ignore

  screen.getByText("Pour plus d'informations contactez nous surou par e-mail à l'addresse.") // prettier-ignore
  screen.getByText("le Slack de CarbuRe")
  screen.getByText("carbure@beta.gouv.fr")
})

test("pick an entity from the menu", async () => {
  render(<CarbureWithRouter />)

  const menu = await screen.findByText("Producteur Test")

  screen.getByText("Stocks", { selector: "a" })
  screen.getByText("Transactions", { selector: "a" })
  screen.getByText("Société", { selector: "a" })

  userEvent.click(menu)

  const entity = await screen.findByText("Opérateur Test")
  userEvent.click(entity)

  await screen.findByTitle("Chargement...")

  expect(menu.textContent).toBe("Opérateur Test")

  expect(screen.queryByText("Stocks")).toBeNull()
})
