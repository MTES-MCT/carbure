import { render } from "setupTests"
import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity } from 'common/types'
import { operator, producer, trader } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { MemoryRouter } from "react-router-dom"
import { DeclarationSummaryPrompt } from "../components/declaration-summary"
import { prettyVolume } from '../helpers'

import server from "./api"

const DeclarationSummary = ({ entity }: { entity: Entity }) => (
  <DeclarationSummaryPrompt
    entityID={entity.id}
    onResolve={() => { }}
  />
)

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("display transaction details", async () => {
  render(<DeclarationSummary entity={producer} />)

  await waitWhileLoading()

  screen.getByText("Déclaration de durabilité")
  screen.getByText("Pour la période")

  screen.getByText("Sorties")
  screen.getByText("Entrées")
  expect(screen.getAllByText((_, node) => node?.textContent == `▸ 1 lot ▸ 12 345 litres`)).toHaveLength(2)

  screen.getByText((_, node) => node?.textContent == "Encore 2 lots en attente de validation pour cette période")
  const button = screen.getByText('Valider ma déclaration').closest('button')
  expect(button).toBeDisabled()
})