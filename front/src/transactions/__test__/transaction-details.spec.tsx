import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { Route } from "common/components/relative-route"
import { Entity } from "common/types"

import { producer } from "common/__test__/data"
import { useTransactions } from "../index"
import TransactionDetails from "../routes/transaction-details"

import server, { setDetails } from "./api"
import { lotDetails } from "./data"

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  setDetails(lotDetails)
})
afterAll(() => server.close())

const TransactionWithHook = ({ entity }: { entity: Entity }) => {
  const { deleter, validator, acceptor, rejector, refresh } = useTransactions(
    entity
  )

  return (
    <Route relative path=":id">
      <TransactionDetails
        entity={entity}
        refresh={refresh}
        deleter={deleter}
        validator={validator}
        acceptor={acceptor}
        rejector={rejector}
      />
    </Route>
  )
}

const TransactionWithRouter = ({ entity }: { entity: Entity }) => (
  <MemoryRouter initialEntries={["/org/0/transactions/draft/0"]}>
    <Route path="/org/0/transactions/:status">
      <TransactionWithHook entity={entity} />
    </Route>
  </MemoryRouter>
)

test("display transaction details", async () => {
  render(<TransactionWithRouter entity={producer} />)

  screen.getByText("Détails de la transaction")

  await screen.findByTitle("Chargement...")

  await screen.findByDisplayValue("DAETEST")

  screen.getByDisplayValue("12345")
  screen.getByDisplayValue("EMHV")
  screen.getByDisplayValue("Colza")
  screen.getByDisplayValue("2020-01-31")
  screen.getByDisplayValue("Producteur Test")
  screen.getByDisplayValue("Test Production Site")
  screen.getByDisplayValue("2000-01-31")
  screen.getByDisplayValue("Opérateur Test")
  screen.getByDisplayValue("Test Delivery Site")
  screen.getByDisplayValue("12")
  screen.getByDisplayValue("1")
  screen.getByDisplayValue("11 gCO2eq/MJ")
  screen.getByDisplayValue("86.87%")

  const countries = screen.getAllByDisplayValue("France")
  const zeros = screen.getAllByDisplayValue("0")

  expect(countries.length).toBe(3)
  expect(zeros.length).toBe(7)

  userEvent.click(screen.getByText("Retour"))
})

test("edit transaction details", async () => {
  render(<TransactionWithRouter entity={producer} />)

  screen.getByText("Détails de la transaction")

  await screen.findByTitle("Chargement...")

  const save: any = await screen.findByText("Sauvegarder")
  expect(save.disabled).toBe(true)

  userEvent.click(screen.getByLabelText("Il s'agit d'une mise à consommation ?")) // prettier-ignore
  const dae = screen.getByLabelText("Numéro douanier (DAE, DAA...)")
  userEvent.clear(dae)
  userEvent.type(dae, "DAETESTUPDATE")

  const vol = screen.getByLabelText("Volume à 20°C en Litres")
  userEvent.clear(vol)
  userEvent.type(vol, "20000")

  const bio = screen.getByLabelText("Biocarburant")
  userEvent.clear(bio)
  userEvent.type(bio, "EM")
  userEvent.click(await screen.findByText("EMHV"))

  const mp = screen.getByLabelText("Matiere Premiere")
  userEvent.clear(mp)
  userEvent.type(mp, "Co")
  userEvent.click(await screen.findByText("Colza"))

  const ct = screen.getByLabelText("Pays d'origine")
  userEvent.clear(ct)
  userEvent.type(ct, "France")

  const dd = screen.getByLabelText("Date de livraison")
  userEvent.clear(dd)
  userEvent.type(dd, "2021-31-01")

  screen.getByDisplayValue("Producteur Test")

  const ps = screen.getByLabelText("Site de production")
  userEvent.clear(ps)
  userEvent.type(ps, "Test")
  userEvent.click(await screen.findByText("Test Production Site"))

  const cli = screen.getByLabelText("Client")
  userEvent.clear(cli)
  userEvent.type(cli, "Test")
  userEvent.click(await screen.findByText("Opérateur Test"))

  const ds = screen.getByLabelText("Site de livraison")
  userEvent.clear(ds)
  userEvent.type(ds, "Test")
  userEvent.click(await screen.findByText("Test Delivery Site"))

  const cl = screen.getByLabelText("Champ Libre")
  userEvent.clear(cl)
  userEvent.type(cl, "blabla")

  const eec = screen.getByLabelText("EEC")
  userEvent.clear(eec)
  userEvent.type(eec, "10")

  const el = screen.getByLabelText("EL")
  userEvent.clear(el)
  userEvent.type(el, "1.1")

  const ep = screen.getByLabelText("EP")
  userEvent.clear(ep)
  userEvent.type(ep, "1.2")

  const etd = screen.getByLabelText("ETD")
  userEvent.clear(etd)
  userEvent.type(etd, "1.3")

  const eu = screen.getByLabelText("EU")
  userEvent.clear(eu)
  userEvent.type(eu, "1.4")

  const esca = screen.getByLabelText("ESCA")
  userEvent.clear(esca)
  userEvent.type(esca, "1.1")

  const eccs = screen.getByLabelText("ECCS")
  userEvent.clear(eccs)
  userEvent.type(eccs, "1.2")

  const eccr = screen.getByLabelText("ECCR")
  userEvent.clear(eccr)
  userEvent.type(eccr, "1.3")

  const eee = screen.getByLabelText("EEE")
  userEvent.clear(eee)
  userEvent.type(eee, "1.4")

  expect(save.disabled).toBe(false)

  userEvent.click(save)

  await screen.findByTitle("Chargement...")

  await screen.findByDisplayValue("DAETESTUPDATE OK")

  userEvent.click(screen.getByText("Retour"))
})

test.todo("check transaction errors")
test.todo("check transaction comments")

test.todo("send draft lot from details")
test.todo("delete draft lot from details")

test.todo("resend tofix lot from details")
test.todo("delete tofix lot from details")

test.todo("accept inbox lot from details")
test.todo("accept sous reserve inbox lot from details")
test.todo("reject inbox lot from details")
