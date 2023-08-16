import { Entity } from "carbure/types"
import { Route } from "react-router-dom"
import { TestRoot } from "setupTests"
import { setEntity } from "settings/__test__/api"

import Transactions from "../index"
import { render, screen } from "@testing-library/react"
import { Data, waitWhileLoading } from "carbure/__test__/helpers"
import { operator } from "carbure/__test__/data"
import server from "./api"
import { emptyLots, emptySnapshot, lots, snapshot } from "./data"
import userEvent from "@testing-library/user-event"
import { clickOnCheckboxesAndConfirm } from "./helpers"

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
beforeEach(() => {
  Data.set("snapshot", snapshot)
  Data.set("lots", lots)
})
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const TransactionsWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: string
}) => {
  setEntity(entity)
  return (
    <TestRoot url={`/org/${entity.id}/transactions/2021/${status}/pending`}>
      <Route
        path={`/org/${entity.id}/transactions/:year/*`}
        element={<Transactions />}
      />
    </TestRoot>
  )
}

test("display an empty list of transactions", async () => {
  Data.set("snapshot", emptySnapshot)
  Data.set("lots", emptyLots)
  render(<TransactionsWithRouter status="drafts" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("Brouillon")
  screen.getByText("Lot reçu")
  screen.getByText("Lot envoyé")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Fournisseurs")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")
  // screen.getByText("Aucun résultat trouvé pour cette recherche")
  screen.getByText("Chargement en cours...")
})

test("display a list of 1 transaction", async () => {
  render(<TransactionsWithRouter status="drafts" entity={operator} />)

  await screen.findByText("30")
  screen.getByText("20")
  screen.getAllByText("10")

  // check column headers
  await screen.findByText("Statut")
  screen.getByText("Période")
  screen.getByText("N° Document")
  screen.getByText("Biocarburant")
  screen.getByText("Matière première")
  screen.getByText("Fournisseur")
  screen.getByText("Client")
  screen.getByText("Site de production")
  screen.getByText("Site de livraison")
  screen.getByText("Réd. GES")

  // check lot columns
  screen.getAllByText("Brouillon")
  screen.getByText("2020-01")
  screen.getByText("EMHV")
  screen.getByText("12 345 litres")
  screen.getByText("Colza")
  screen.getByText("Producteur Test")
  screen.getByText("Test Production Site")
  screen.getByText("Test Delivery Site")
  const countries = screen.getAllByText("France")
  expect(countries.length).toBe(3)
})

test("check draft actions", async () => {
  render(<TransactionsWithRouter status="drafts" entity={operator} />)

  // check global actions
  await screen.findByText("Créer un lot")
  screen.getByText("Importer des lots")
  screen.getByText("Envoyer tout")
  screen.getByText("Supprimer tout")
  screen.getByText("Exporter vers Excel")

  await screen.findByText("2021")
})

test("check inbox actions", async () => {
  const user = userEvent.setup()

  render(<TransactionsWithRouter status="in" entity={operator} />)

  await waitWhileLoading()

  await user.click(screen.getByText("En attente (0)"))

  // check global actions
  screen.getByText("Accepter tout")
  screen.getByText("Refuser tout")
  screen.getByText("Exporter vers Excel")

  await screen.findByText("2021")
})

test("check outbox actions", async () => {
  const user = userEvent.setup()

  render(<TransactionsWithRouter status="out" entity={operator} />)

  await waitWhileLoading()
  screen.getByText("Exporter vers Excel")

  await user.click(screen.getByText("En attente (0)"))

  screen.getByText("Corriger la sélection")

  await user.click(screen.getByText("Corrections (0)"))

  screen.getByText("Confirmer les corrections")
  screen.getByText("Supprimer la sélection")

  await screen.findByText("2021")
})

test("send all draft lots", async () => {
  const user = userEvent.setup()

  render(<TransactionsWithRouter status="drafts" entity={operator} />)

  await screen.findByText("2021")
  const button = (await screen.findByText("Envoyer tout")).closest("button")!

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  expect(button).not.toBeDisabled()

  // click on the send all button
  await user.click(button)

  // confirm the sending
  const title = screen.getByText("Envoyer tous les brouillons")
  await clickOnCheckboxesAndConfirm(user)

  await waitWhileLoading()

  expect(title).not.toBeInTheDocument()

  // decreased amount of draft lots
  await screen.findByText("29")
  // increased amount of received lots
  screen.getByText("11")

  // no more drafts
  await screen.findByText("Aucun résultat trouvé pour cette recherche")
})

test("sent selected draft lots", async () => {
  const user = userEvent.setup()

  render(<TransactionsWithRouter status="drafts" entity={operator} />)

  await waitWhileLoading()

  screen.getByText("2021")

  // select the first lot
  await user.click(document.querySelector("li [data-checkbox]")!)

  // click on the send selection button
  await user.click(screen.getByText("Envoyer sélection"))

  // confirm the sending
  const title = screen.getByText("Envoyer ce brouillon")
  await clickOnCheckboxesAndConfirm(user)

  await waitWhileLoading()

  expect(title).not.toBeInTheDocument()

  // decreased amount of draft lots
  await screen.findByText("29")
  // increased amount of received lots
  screen.getByText("11")

  // no more drafts
  await screen.findByText("Aucun résultat trouvé pour cette recherche")
})
