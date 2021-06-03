import { render, TestRoot } from "setupTests"
import { screen } from "@testing-library/react"

import { Entity } from "common/types"
import { producer } from "common/__test__/data"
import { waitWhileLoading } from "common/__test__/helpers"
import { DeclarationSummaryPrompt } from "../components/declaration-summary"

import server from "./api"

const DeclarationSummary = ({ entity }: { entity: Entity }) => (
  <TestRoot url={`/org/${entity.id}`}>
    <DeclarationSummaryPrompt entityID={entity.id} onResolve={() => {}} />
  </TestRoot>
)

beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test("display transaction details", async () => {
  render(<DeclarationSummary entity={producer} />)

  await waitWhileLoading()

  screen.getByText("Déclaration de durabilité")
  screen.getByText("Pour la période")

  await screen.findByText("Sorties")
  await screen.findByText("Entrées")

  expect(
    screen.getAllByText(
      (_, node) => node?.textContent === `▸ 1 lot ▸ 12 345 litres`
    )
  ).toHaveLength(2)

  screen.getByText(
    (_, node) =>
      node?.textContent ===
      "Encore 2 lots en attente de validation pour cette période"
  )
  const button = screen.getByText("Valider ma déclaration").closest("button")
  expect(button).toBeDisabled()
})
