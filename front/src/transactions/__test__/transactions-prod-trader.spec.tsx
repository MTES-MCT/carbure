import { render } from "setupTests"
import { waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "common/components/relative-route"
import { Entity, LotStatus } from "common/types"

import { producer } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import Transactions from "../index"
import { clickOnCheckboxesAndConfirm } from "./helpers"

import server, { setLots, setSnapshot } from "./api"
import {
  deadlineLots,
  emptyLots,
  emptySnapshot,
  errorLots,
  lots,
  manyLots,
  snapshot,
} from "./data"

const TransactionsWithRouter = ({
  entity,
  status,
}: {
  entity: Entity
  status: LotStatus
}) => (
  <MemoryRouter initialEntries={[`/org/0/transactions/${status}`]}>
    <Route path="/org/0/transactions/:status">
      <Transactions entity={entity} />
    </Route>
  </MemoryRouter>
)

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  setSnapshot(snapshot)
  setLots(lots)
})

afterAll(() => server.close())

test("producer/trader: display an empty list of transactions", async () => {
  setSnapshot(emptySnapshot)
  setLots(emptyLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("Brouillons")
  screen.getByText("Lots envoyés")
  screen.getByText("Lots à corriger")
  screen.getByText("Lots acceptés")

  const quantities = await screen.findAllByText("0")
  expect(quantities.length).toBe(4)

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Clients")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: display a list of 1 transaction", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("40")
  screen.getByText("30")
  screen.getByText("20")
  screen.getAllByText("10")

  // check column headers
  screen.getByText("Statut")
  screen.getByText("Période")
  screen.getByText("N° Douane")
  screen.getByText("Biocarburant (litres)")
  screen.getByText("Matiere premiere")
  screen.getByText("Client")
  screen.getByText("Site de production")
  screen.getByText("Site de livraison")
  screen.getByText("Réd. GES")

  // check lot columns
  screen.getByText("Brouillon")
  screen.getByText("2020-01")
  screen.getByText("EMHV")
  screen.getByText("12 345")
  screen.getByText("Colza")
  screen.getByText("Opérateur Test")
  screen.getByText("Test Production Site")
  screen.getByText("Test Delivery Site")
  screen.getByText("France, Test City")
  const countries = screen.getAllByText("France")
  expect(countries).toHaveLength(2)
})

test("producer/trader: check filters", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  const filters = [
    { name: "Périodes", value: "2020-01" },
    { name: "Biocarburants", value: "EMHV" },
    { name: "Matières Premières", value: "Colza" },
    { name: "Clients", value: "Opérateur Test" },
    { name: "Pays d'origine", value: "France" },
    { name: "Sites de production", value: "Test Production Site" },
    { name: "Sites de livraison", value: "Test Delivery Site" },
  ]

  for (let i = 0; i < filters.length; i++) {
    const { name, value } = filters[i]

    // locate the wanted filter
    const filter = await screen.findByText(name)

    // open the filter list
    userEvent.click(filter)

    // select a value from the list
    const selection = await screen.findByText(value, { selector: "li span" }) // prettier-ignore
    userEvent.click(selection)

    await waitWhileLoading()

    userEvent.type(filter, "{esc}")

    // close the dropdown
    expect(selection).not.toBeInTheDocument()

    // check that the right selection is displayed
    await screen.findByText(value, { selector: ".selectValue" })
  }
})

test("check search filter", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("DAETEST")

  userEvent.type(screen.getByPlaceholderText("Rechercher..."), "test")

  await screen.findByTitle("Chargement...")
})

test("check year filter", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  await screen.findByText("DAETEST")

  userEvent.click(screen.getByText("2020"))
  userEvent.click(screen.getByText("2019"))

  await screen.findByTitle("Chargement...")
})

test("check pagination", async () => {
  setLots(manyLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  await screen.findAllByText("DAETEST")

  const select = screen.getByText("1", { selector: ".selectValue" })
  const prev = screen.getByTitle("Page précédente")
  const next = screen.getByTitle("Page suivante")

  screen.getByText("sur 20,")

  expect(prev).toBeDisabled()

  // select a page from the dropdown
  userEvent.click(select)
  userEvent.click(screen.getByText("19"))

  await waitWhileLoading()

  expect(select).toHaveTextContent("19")
  expect(prev).not.toBeDisabled()

  // click on the next button
  userEvent.click(next)

  await waitWhileLoading()

  await screen.findByText("20", { selector: ".selectValue" })
  expect(next).toBeDisabled()

  // click on the prev button
  userEvent.click(prev)

  await waitWhileLoading()

  await screen.findByText("19", { selector: ".selectValue" })
  expect(next).not.toBeDisabled()
})

test("check error filter", async () => {
  setLots(errorLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  const dae = await screen.findByText("DAETEST")

  expect(dae.closest(".tableRow")).toHaveClass("transactionRowError")

  await screen.findByText(
    (content, node) =>
      node.textContent ===
      "Parmi ces résultats, 1 lot présente des incohérences"
  )

  userEvent.click(screen.getByText("Voir la liste"))

  await waitWhileLoading()

  await screen.findByText(
    (content, node) => node.textContent === "1 lot présente des incohérences"
  )

  userEvent.click(screen.getByText("Revenir à la liste complète"))

  await waitWhileLoading()

  await screen.findByText("Voir la liste")
})

test("check deadline filter", async () => {
  setLots(deadlineLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  const dae = await screen.findByText("DAETEST")

  expect(dae.closest(".tableRow")).toHaveClass("transactionRowDeadline")

  await screen.findByText(
    (content, node) =>
      node.textContent ===
      "Parmi ces résultats, 1 lot doit être validé et envoyé avant le 29 février"
  )

  userEvent.click(screen.getByText("Voir la liste"))

  await waitWhileLoading()

  await screen.findByText(
    (content, node) =>
      node.textContent ===
      "1 lot doit être validé et envoyé avant le 29 février"
  )

  userEvent.click(screen.getByText("Revenir à la liste complète"))

  await waitWhileLoading()

  await screen.findByText("Voir la liste")
})

test("producer/trader: check draft actions", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // check global actions
  await screen.findByText("Exporter")
  screen.getByText("Importer lots")
  screen.getByText("Créer lot")
  screen.getByText("Envoyer tout")
  screen.getByText("Supprimer tout")

  // check row actions
  screen.getByTitle("Envoyer le lot")
  screen.getByTitle("Dupliquer le lot")
  screen.getByTitle("Supprimer le lot")
})

test("producer/trader: check sent actions", async () => {
  render(
    <TransactionsWithRouter status={LotStatus.Validated} entity={producer} />
  )

  await waitWhileLoading()

  // check global actions
  await screen.findByText("Exporter")

  // check row actions
  screen.getByTitle("Dupliquer le lot")
})

test("producer/trader: check tofix actions", async () => {
  render(<TransactionsWithRouter status={LotStatus.ToFix} entity={producer} />)

  await waitWhileLoading()

  // check global actions
  await screen.findByText("Exporter")
  screen.getByText("Supprimer sélection")

  // check row actions
  screen.getByTitle("Renvoyer le lot")
  screen.getByTitle("Supprimer le lot")
})

test("producer/trader: check accepted actions", async () => {
  render(
    <TransactionsWithRouter status={LotStatus.Accepted} entity={producer} />
  )

  await waitWhileLoading()

  // check global actions
  await screen.findByText("Exporter")

  // check row actions
  screen.getByTitle("Dupliquer le lot")
})

test("producer/trader: duplicate draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // click on the duplicate action
  const duplicate = await screen.findByTitle("Dupliquer le lot")
  userEvent.click(duplicate)

  // confirm the duplication
  const title = screen.getByText("Dupliquer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // number in snapshot was incremented
  await screen.findByText("41")

  // new line was added
  await waitFor(() => expect(screen.getAllByText("Brouillon")).toHaveLength(2))
  expect(screen.getAllByText("2020-01")).toHaveLength(2)
  expect(screen.getAllByText("EMHV")).toHaveLength(2)
  expect(screen.getAllByText("12 345")).toHaveLength(2)
  expect(screen.getAllByText("Colza")).toHaveLength(2)
  expect(screen.getAllByText("Opérateur Test")).toHaveLength(2)
  expect(screen.getAllByText("Test Production Site")).toHaveLength(2)
  expect(screen.getAllByText("Test Delivery Site")).toHaveLength(2)
  expect(screen.getAllByText("France, Test City")).toHaveLength(2)
  expect(screen.getAllByText("France")).toHaveLength(4)
})

// SEND DRAFT

test("producer/trader: sent draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByTitle("Envoyer le lot")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Envoyer lot")
  clickOnCheckboxesAndConfirm()

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of draft lots
  await screen.findByText("39")
  // increased amount of sent lots
  screen.getByText("31")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: sent all draft lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  const button = screen.getByText("Envoyer tout").closest("button")!
  expect(button).toBeDisabled()

  await waitWhileLoading()

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  expect(button).not.toBeDisabled()

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  const title = screen.getByText("Envoyer tous les brouillons")
  clickOnCheckboxesAndConfirm()

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of draft lots
  await screen.findByText("39")
  // increased amount of sent lots
  screen.getByText("31")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: sent selected draft lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Envoyer sélection"))

  // confirm the sending
  const title = screen.getByText("Envoyer la sélection")
  clickOnCheckboxesAndConfirm()

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of draft lots
  await screen.findByText("39")
  // increased amount of sent lots
  screen.getByText("31")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

// DELETE DRAFT

test("producer/trader: delete draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByTitle("Supprimer le lot")
  userEvent.click(send)

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of draft lots
  await screen.findByText("39")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: delete all draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  const button = screen.getByText("Supprimer tout").closest("button")!
  expect(button).toBeDisabled()

  await waitWhileLoading()

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  expect(button).not.toBeDisabled()

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  await screen.findByText("39")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: delete selected draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={producer} />)

  await waitWhileLoading()

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Supprimer sélection"))

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  await screen.findByText("39")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

// RESEND TOFIX

test("producer/trader: resend fixed lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.ToFix} entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByTitle("Renvoyer le lot")
  userEvent.click(send)

  // confirm the fix by adding a comment
  const title = screen.getByText("Envoyer lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "ok")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of lots to fix
  await screen.findByText("19")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

// DELETE TOFIX

test("producer/trader: delete tofix lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.ToFix} entity={producer} />)

  await waitWhileLoading()

  // click on the send action
  const send = await screen.findByTitle("Supprimer le lot")
  userEvent.click(send)

  // confirm the removal
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of lots to fix
  await screen.findByText("19")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})

test("producer/trader: delete selected tofix lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.ToFix} entity={producer} />)

  await waitWhileLoading()

  // wait for the lot to be loaded
  await screen.findByText("DAETEST")

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Supprimer sélection"))

  // confirm the sending
  const title = screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  expect(title).not.toBeInTheDocument()

  await waitWhileLoading()

  // decreased amount of tofix lots
  await screen.findByText("19")

  // no more tofix lots
  await screen.findByText("Aucune transaction trouvée pour cette recherche")
})
