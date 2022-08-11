import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"

import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import Auth from "auth"
import { getField, waitWhileLoading } from "carbure/__test__/helpers"
import server from "./api"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const AuthWithRouter = ({ children }: { children?: React.ReactNode }) => {
  return (
    <TestRoot url={`/auth/login`}>
      <Route path="/auth/*" element={<Auth />} />
    </TestRoot>
  )
}

test("display the login form", async () => {
  render(<AuthWithRouter />)
  await waitWhileLoading()
  await screen.findByText("→ Connexion")
  await screen.findByText("→ Inscription")
  await screen.findByText("Adresse email")
  await screen.findByText("Mot de passe")
  await screen.findByText("J'ai oublié mon mot de passe")
  await screen.findByText("Se connecter au compte")
})

test("Switch to the register form", async () => {
  render(<AuthWithRouter />)
  const user = userEvent.setup()
  await screen.findByText("→ Inscription")
  await user.click(await screen.findByText("→ Inscription"))
  await screen.findByText("Créer un nouveau compte")
})

test("fill and submit the login form", async () => {
  render(<AuthWithRouter />)
  const user = userEvent.setup()
  await user.type(getField("Adresse email"), "test@company.com")
  await user.type(getField("Mot de passe"), "azerty")
  await user.click(await screen.findByText("Se connecter au compte"))
  await screen.findByText("Code reçu par email")
})

test("want to reset password", async () => {
  render(<AuthWithRouter />)
  const user = userEvent.setup()

  await user.click(await screen.findByText("J'ai oublié mon mot de passe"))
  await user.type(getField("Adresse email du compte"), "test@company.com")
  await user.click(await screen.findByText("Demander une réinitialisation"))
  await screen.findByText(/Votre demande de réinitialisation de mot de passe/)
})
