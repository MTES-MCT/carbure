import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"

import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { ActivateRequest } from "auth/components/activate"
import { getField, waitWhileLoading } from "carbure/__test__/helpers"
import { Register, RegisterPending } from "../components/register"
import server from "./api"
import Auth from "auth"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const AuthWithRouter = ({ children }: { children?: React.ReactNode }) => {
	return (
		<TestRoot url={`/auth/register`}>
			<Route path="/auth/*" element={<Auth />} />
		</TestRoot>
	)
}

test("display the register form", async () => {
	render(<AuthWithRouter />)
	await waitWhileLoading()
	await screen.findByText("Adresse email")
	await screen.findByText("Nom")
	await screen.findByText("Mot de passe")
	await screen.findByText("Répéter le mot de passe")
})

test("fill and submit the register form", async () => {
	render(<AuthWithRouter />)

	const user = userEvent.setup()
	await user.type(getField("Adresse email"), "test@company.com")
	await user.type(getField("Nom"), "Jean-Pierre Champollion")
	await user.type(getField("Mot de passe"), "azerty")
	await user.type(getField("Répéter le mot de passe"), "azerty")
	await user.click(await screen.findByText("Créer un nouveau compte"))
	await waitWhileLoading()
	await screen.findByText(/Votre demande d'inscription a bien été envoyée/)
})

test("resend activation link", async () => {
	render(<AuthWithRouter />)
	const user = userEvent.setup()
	await user.click(await screen.findByText("Je n'ai pas reçu le lien d'activation")) // prettier-ignore
	await screen.findByText(/Veuillez renseigner votre adresse email/)
	await user.type(getField("Adresse email du compte"), "test@company.com")
	await user.click(await screen.findByText("Renvoyer le lien d'activation"))
	await screen.findByText(/Votre demande d'inscription a bien été envoyée/)
})
