import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"

import { render, screen } from "@testing-library/react"
import Login from "auth/components/login"
import server from "./api"
import userEvent from "@testing-library/user-event"
import { getField, waitWhileLoading } from "carbure/__test__/helpers"
import OTP from "auth/components/otp"
import { Register } from "../components/register"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const AuthWithRouter = ({ children }: { children?: React.ReactNode }) => {
  return (
    <TestRoot url={`/app/auth/login`}>
      <Route path={`/app/auth/login`} element={<Login />} />
      {children}
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

test("Switch to register", async () => {
  render(
    <AuthWithRouter>
      <Route path={`/register`} element={<Register />} />
    </AuthWithRouter>
  )
  const user = userEvent.setup()
  await screen.findByText("→ Inscription")
  await user.click(await screen.findByText("→ Inscription"))
  await screen.findByText("Créer un nouveau compte")
})

// test("will fill and submit the forme", async () => {
//   render(
//     <AuthWithRouter>
//       <Route path={`/otp`} element={<OTP />} />
//     </AuthWithRouter>
//   )
//   const user = userEvent.setup()
//   await user.type(getField("Adresse email"), "damien@coton.fr")
//   await user.type(getField("Mot de passe"), "azerty")
//   await user.click(await screen.findByText("Se connecter au compte"))

//   await waitWhileLoading()
//   await screen.findByText("Code reçu par email")
// })
