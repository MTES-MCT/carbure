import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { Operation, OperationType } from "accounting/types"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"
import { useOperationDetailFields } from "./operation-detail-fields.hooks"

vi.mock("react-i18next", async (importOriginal) => ({
  ...(await importOriginal<typeof import("react-i18next")>()),
  useTranslation: () => ({ t: (value: string) => value }),
}))

const makeOperation = (overrides: Partial<Operation> = {}): Operation =>
  ({
    ...operationCredit,
    type: OperationType.INCORPORATION,
    volume: 1000,
    energy: 27000,
    avoided_emissions: 100,
    renewable_energy_share: 0.5,
    ...overrides,
  }) as Operation

const findFieldValue = (
  fields: Array<{ label: string; value: unknown }>,
  label: string
) => fields.find((field) => field.label === label)?.value

describe("useOperationDetailFields", () => {
  it("shows quantity in liters and renewable energy in GJ when renewable share is partial", () => {
    const operation = makeOperation({ renewable_energy_share: 0.5 })

    const { result } = renderHook(() => useOperationDetailFields(operation))

    const quantity = findFieldValue(result.current, "Quantité")
    const renewableEnergy = findFieldValue(
      result.current,
      "Energie renouvelable"
    )

    expect(quantity).toBe("+1 000 litres")
    expect(renewableEnergy).toBe("+27 GJ")
  })

  it("does not add renewable energy field when renewable share is 100 percent", () => {
    const operation = makeOperation({ renewable_energy_share: 1 })

    const { result } = renderHook(() => useOperationDetailFields(operation))

    const quantity = findFieldValue(result.current, "Quantité")
    const renewableEnergy = findFieldValue(
      result.current,
      "Energie renouvelable"
    )

    expect(quantity).toBe("+1 000 litres / +27 GJ")
    expect(renewableEnergy).toBeUndefined()
  })

  it("keeps full avoided emissions value", () => {
    const operation = makeOperation({
      renewable_energy_share: 0.5,
      avoided_emissions: 120,
    })

    const { result } = renderHook(() => useOperationDetailFields(operation))

    const avoidedEmissions = findFieldValue(
      result.current,
      "Tonnes CO2 eq évitées"
    )

    expect(String(avoidedEmissions)).toContain("120")
    expect(String(avoidedEmissions)).not.toContain("60")
  })
})
