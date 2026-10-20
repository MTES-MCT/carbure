import {
  act,
  cleanup,
  fireEvent,
  render,
  renderHook,
} from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import Form from "common/components/form"
import useEntity, { EntityManager } from "common/hooks/entity"
import { Depot } from "common/types"
import { DeliveryType, FuelUsage, Lot, LotStatus } from "transactions/types"
import { ClientField, DeliverySiteField } from "./delivery-fields"
import { lotFormToPayload, useLotForm } from "./lot-form"

vi.mock("common/hooks/entity", () => ({ default: vi.fn() }))

vi.mock("react-i18next", async (importOriginal) => ({
  ...(await importOriginal<typeof import("react-i18next")>()),
  useTranslation: () => ({ t: (value: string) => value }),
}))

const operator = {
  id: 2,
  name: "Recipient",
  isOperator: true,
  has_direct_deliveries: true,
  preferred_unit: "l",
  default_certificate: "CERT",
} as EntityManager
const supplier = { ...operator, id: 1, name: "Supplier" }
const admin = { ...operator, id: 3, isOperator: false, isAdmin: true }
const depot = { id: 10, name: "Delivery depot", customs_id: "DEPOT" } as Depot

function directLot(overrides: Partial<Lot> = {}): Lot {
  return {
    id: 1,
    added_by: supplier,
    carbure_supplier: supplier,
    carbure_client: operator,
    carbure_delivery_site: depot,
    delivery_type: DeliveryType.Direct,
    lot_status: LotStatus.Accepted,
    usage: FuelUsage.Road,
    ...overrides,
  } as Lot
}

beforeEach(() => vi.mocked(useEntity).mockReturnValue(operator))
afterEach(cleanup)

describe("DIRECT supplier defaults", () => {
  it.each([
    { status: LotStatus.Accepted, viewer: operator, owner: supplier },
    { status: LotStatus.Frozen, viewer: operator, owner: supplier },
    { status: LotStatus.Draft, viewer: admin, owner: supplier },
    { status: LotStatus.Draft, viewer: operator, owner: supplier },
  ])(
    "preserves the supplier for $status lots viewed by $viewer.name",
    ({ status, viewer, owner }) => {
      vi.mocked(useEntity).mockReturnValue(viewer)
      const lot = directLot({ lot_status: status, added_by: owner })
      const { result } = renderHook(() => useLotForm(lot))

      expect(result.current.value.supplier).toEqual(supplier)
      expect(lotFormToPayload(result.current.value).carbure_supplier_id).toBe(
        supplier.id
      )
    }
  )

  it("defaults to the current entity when selecting DIRECT on a new lot", () => {
    const { result } = renderHook(() => useLotForm())
    act(() => result.current.setField("delivery_type", DeliveryType.Direct))

    expect(result.current.value.supplier).toEqual(operator)
    expect(result.current.value.delivery_site_country?.code_pays).toBe("FR")
  })

  it("defaults to the owner when editing their DIRECT draft", () => {
    const lot = directLot({ lot_status: LotStatus.Draft, added_by: operator })
    const { result } = renderHook(() => useLotForm(lot))

    expect(result.current.value.supplier).toEqual(operator)
  })
})

describe("DIRECT delivery text fields", () => {
  it.each([
    { Component: ClientField, text: operator.name },
    { Component: DeliverySiteField, text: depot.name },
  ])(
    "displays the recorded name $text without changing its identifier",
    ({ Component, text }) => {
      const lot = directLot()
      const { result } = renderHook(() => useLotForm(lot))
      const { getByRole } = render(
        <Form form={result.current}>
          <Component readOnly />
        </Form>
      )

      expect((getByRole("textbox") as HTMLInputElement).value).toBe(text)
      const payload = lotFormToPayload(result.current.value)
      expect(payload.carbure_client_id).toBe(operator.id)
      expect(payload.carbure_delivery_site_depot_id).toBe(depot.customs_id)
    }
  )

  it("displays the default operator client when switching to DIRECT", () => {
    const { result } = renderHook(() => useLotForm())
    act(() => result.current.setField("delivery_type", DeliveryType.Direct))
    const { getByRole } = render(
      <Form form={result.current}>
        <ClientField />
      </Form>
    )

    expect((getByRole("textbox") as HTMLInputElement).value).toBe(operator.name)
  })

  it.each([
    {
      Component: ClientField,
      field: "client" as const,
      text: "External client",
    },
    {
      Component: DeliverySiteField,
      field: "delivery_site" as const,
      text: "External depot",
    },
  ])("allows entering a free-text $field", ({ Component, field, text }) => {
    const lot = directLot()
    const { result } = renderHook(() => useLotForm(lot))
    const { getByRole } = render(
      <Form form={result.current}>
        <Component />
      </Form>
    )
    fireEvent.change(getByRole("textbox"), { target: { value: text } })

    expect(result.current.value[field]).toBe(text)
  })
})
