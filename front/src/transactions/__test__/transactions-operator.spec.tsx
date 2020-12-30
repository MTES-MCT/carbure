import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Route } from "common/components/relative-route"
import { Entity, LotStatus } from "common/types"

import { operator } from "common/__test__/data"
import { MemoryRouter } from "react-router-dom"
import Transactions from "../index"

import server, { setLots, setSnapshot } from "./api"
import { emptyLots, lots, operatorSnapshot } from "./data"

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
  setSnapshot(operatorSnapshot)
  setLots(lots)
})

afterAll(() => server.close())

test("operator: display an empty list of transactions", async () => {
  setSnapshot(operatorSnapshot)
  setLots(emptyLots)

  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  screen.getByText("Brouillons")
  screen.getByText("Lots reçus")
  screen.getByText("Lots acceptés")

  screen.getByText("Périodes")
  screen.getByText("Biocarburants")
  screen.getByText("Matières Premières")
  screen.getByText("Fournisseurs")
  screen.getByText("Pays d'origine")
  screen.getByText("Sites de production")
  screen.getByText("Sites de livraison")

  screen.getByPlaceholderText("Rechercher...")

  screen.getByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: display a list of 1 transaction", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  await waitFor(() => {
    screen.getByText("30")
    screen.getByText("20")
    screen.getByText("10")
  })

  // wait for lots to be loaded
  await waitFor(() => {
    // check column headers
    screen.getByText("Statut")
    screen.getByText("Période")
    screen.getByText("N° Douane")
    screen.getByText("Biocarburant (litres)")
    screen.getByText("Matiere premiere")
    screen.getByText("Fournisseur")
    screen.getByText("Site de production")
    screen.getByText("Dépôt")
    screen.getByText("Réd. GES")

    // check lot columns
    screen.getByText("Brouillon")
    screen.getByText("2020-01")
    screen.getByText("EMHV")
    screen.getByText("12 345")
    screen.getByText("Colza")
    screen.getByText("Producteur Test")
    screen.getByText("Test Production Site")
    screen.getByText("Test Delivery Site")
    screen.getByText("France, Test City")
    const countries = screen.getAllByText("France")
    expect(countries.length).toBe(2)
  })
})

test("operator: check draft actions", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // wait for lots to be loaded
  await waitFor(() => {
    // check global actions
    screen.getByText("Exporter")
    screen.getByText("Importer lots")
    screen.getByText("Créer lot")
    screen.getByText("Envoyer tout")
    screen.getByText("Supprimer tout")

    // check row actions
    screen.getByTitle("Envoyer le lot")
    screen.getByTitle("Dupliquer le lot")
    screen.getByTitle("Supprimer le lot")
  })
})

test("operator: check inbox actions", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // wait for lots to be loaded
  await waitFor(() => {
    // check global actions
    screen.getByText("Exporter")
    screen.getByText("Rapport d'entrées")
    screen.getByText("Accepter tout")
    screen.getByText("Refuser tout")

    // check row actions
    screen.getByTitle("Accepter le lot")
    screen.getByTitle("Accepter sous réserve")
    screen.getByTitle("Refuser le lot")
  })
})

test("operator: check accepted actions", async () => {
  render(
    <TransactionsWithRouter status={LotStatus.Accepted} entity={operator} />
  )

  screen.findByText("Exporter")
})

test("operator: duplicate draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // click on the duplicate action
  const duplicate = await waitFor(() => screen.getByTitle("Dupliquer le lot"))
  userEvent.click(duplicate)

  // confirm the duplication
  screen.getByText("Dupliquer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  // number in snapshot was incremented
  await screen.findByText("31")

  await waitFor(() => {
    // new line was added
    expect(screen.getAllByText("Brouillon").length).toBe(2)
    expect(screen.getAllByText("2020-01").length).toBe(2)
    expect(screen.getAllByText("EMHV").length).toBe(2)
    expect(screen.getAllByText("12 345").length).toBe(2)
    expect(screen.getAllByText("Colza").length).toBe(2)
    expect(screen.getAllByText("Producteur Test").length).toBe(2)
    expect(screen.getAllByText("Test Production Site").length).toBe(2)
    expect(screen.getAllByText("Test Delivery Site").length).toBe(2)
    expect(screen.getAllByText("France, Test City").length).toBe(2)
    expect(screen.getAllByText("France").length).toBe(4)
  })
})

// SEND DRAFT

test("operator: sent draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // click on the send action
  const send = await screen.findByTitle("Envoyer le lot")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Envoyer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
    // increased amount of received lots
    screen.getByText("21")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: sent all draft lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  const button = screen.getByText("Envoyer tout").closest("button")!

  expect(button.disabled).toBe(true)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  expect(button.disabled).toBe(false)

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  screen.getByText("Envoyer tous les brouillons")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
    // increased amount of received lots
    screen.getByText("21")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: sent selected draft lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Envoyer sélection"))

  // confirm the sending
  screen.getByText("Envoyer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
    // increased amount of sent lots
    screen.getByText("21")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

// DELETE DRAFT

test("operator: delete draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // click on the send action
  const send = await screen.findByTitle("Supprimer le lot")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: delete all draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  const button = screen.getByText("Supprimer tout").closest("button")!

  expect(button.disabled).toBe(true)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  expect(button.disabled).toBe(false)

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: delete selected draft lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Draft} entity={operator} />)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Supprimer sélection"))

  // confirm the sending
  screen.getByText("Supprimer lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("29")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

// ACCEPT INBOX

test("operator: accept inbox lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // click on the send action
  const send = await screen.findByTitle("Accepter le lot")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of inbox lots
    screen.getByText("19")
    // increased amount of accepted lots
    screen.getByText("11")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: accept inbox lot (sous réserve)", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // click on the send action
  const send = await screen.findByTitle("Accepter sous réserve")
  userEvent.click(send)

  // confirm the sending
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByLabelText("Les deux"))
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "not ok")
  userEvent.click(screen.getByText("Accepter et demander une correction"))

  await screen.findByTitle("Chargement...")

  // lot status has changed
  await screen.findByText("À corriger")
})

test("operator: accept all inbox lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  const button = screen.getByText("Accepter tout").closest("button")!

  expect(button.disabled).toBe(true)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  expect(button.disabled).toBe(false)

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("19")
    // increased amount of received lots
    screen.getByText("11")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: accept selected inbox lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Accepter sélection"))

  // confirm the sending
  screen.getByText("Accepter lot")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of draft lots
    screen.getByText("19")
    // increased amount of sent lots
    screen.getByText("11")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

// REJECT INBOX

test("operator: reject inbox lot", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // click on the send action
  const reject = await screen.findByTitle("Refuser le lot")
  userEvent.click(reject)

  // confirm the sending
  screen.getByText("Refuser lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "not ok")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  await waitFor(() => {
    // decreased amount of inbox lots
    screen.getByText("19")
  })

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: reject all inbox lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  const button = screen.getByText("Refuser tout").closest("button")!

  expect(button.disabled).toBe(true)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  expect(button.disabled).toBe(false)

  // click on the send all button
  userEvent.click(button)

  // confirm the sending
  screen.getByText("Refuser lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "not ok")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  // decreased amount of draft lots
  await screen.findByText("19")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})

test("operator: reject selected inbox lots", async () => {
  render(<TransactionsWithRouter status={LotStatus.Inbox} entity={operator} />)

  // wait for the lot to be loaded
  await waitFor(() => screen.getByText("DAETEST"))

  // select the first lot
  userEvent.click(screen.getByTitle("Sélectionner le lot"))

  // click on the send selection button
  userEvent.click(screen.getByText("Refuser sélection"))

  // confirm the sending
  screen.getByText("Refuser lot")
  userEvent.type(screen.getByLabelText("Commentaire (obligatoire)"), "not ok")
  userEvent.click(screen.getByText("OK"))

  await screen.findByTitle("Chargement...")

  // decreased amount of draft lots
  await screen.findByText("19")

  // no more drafts
  await screen.findByText("Aucune transaction trouvée pour ces paramètres")
})
