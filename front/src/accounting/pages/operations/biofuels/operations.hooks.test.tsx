import { renderHook } from "@testing-library/react"
import { renderToStaticMarkup } from "react-dom/server"
import { describe, expect, it, vi } from "vitest"
import {
  OperationList,
  OperationOrder,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import { useOperationsBiofuelsColumns } from "./operations.hooks"

vi.mock("react-i18next", async (importOriginal) => ({
  ...(await importOriginal<typeof import("react-i18next")>()),
  useTranslation: () => ({ t: (value: string) => value }),
}))

vi.mock("common/hooks/unit", () => ({
  useUnit: () => ({ unit: "l" }),
}))

const normalizeText = (markup: string) =>
  markup
    .replace(/<[^>]+>/g, "")
    .replace(/\s/g, "")
    .replace(/,/g, ".")

const makeOperation = (overrides: Partial<OperationList> = {}): OperationList =>
  ({
    volume: 1000,
    avoided_emissions: 120,
    renewable_energy_share: 0.5,
    type: OperationType.INCORPORATION,
    status: "DRAFT" as OperationsStatus,
    ...overrides,
  }) as OperationList

describe("useOperationsBiofuelsColumns", () => {
  it("displays full physical volume for incorporation operations", () => {
    const { result } = renderHook(() =>
      useOperationsBiofuelsColumns({ onClickSector: vi.fn() })
    )

    const volumeColumn = result.current.find(
      (column) => column.key === OperationOrder.volume
    )
    expect(volumeColumn).toBeDefined()

    const operation = makeOperation()
    const markup = renderToStaticMarkup(volumeColumn!.cell(operation))
    const text = normalizeText(markup)

    expect(text).toContain("+1000")
    expect(text).not.toContain("+500")
  })

  it("displays full avoided emissions for incorporation operations", () => {
    const { result } = renderHook(() =>
      useOperationsBiofuelsColumns({ onClickSector: vi.fn() })
    )

    const co2Column = result.current.find(
      (column) => column.header === "tCO2 évitées"
    )
    expect(co2Column).toBeDefined()

    const operation = makeOperation()
    const markup = renderToStaticMarkup(co2Column!.cell(operation))
    const text = normalizeText(markup)

    expect(text).toContain("+120")
    expect(text).not.toContain("+60")
  })
})
