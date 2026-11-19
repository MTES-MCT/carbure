import { Meta, StoryObj } from "@storybook/react"
import { COMMON_MOCKS } from "@storybook/mocks/common"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { balance } from "accounting/__test__/data/balances"
import {
  baseHandlers as quantityHandlers,
  fillQuantityForm,
} from "accounting/components/quantity-form/quantity-form.stories.utils"
import { setGHGRangeValue } from "accounting/components/ghg-range-form/ghg-range-form.stories.utils"
import { Debt } from "accounting/types"
import { apiTypes } from "common/services/api-fetch.types"
import { useUser } from "common/hooks/user"
import { http, HttpResponse } from "msw"
import { ComponentProps } from "react"
import { DebtRepaymentDialog } from "./debt-repayment-dialog"

const debt: Debt = {
  biofuel: balance.biofuel,
  customs_category: balance.customs_category,
  remaining_volume: 0,
  remaining_tco2: 20,
}

const simulation: apiTypes["DebtRepaymentSimulation"] = {
  selected_lots: Array.from({ length: 300 }, (_, index) => ({
    lot_id: index + 1,
    volume: "10.00",
  })),
  total_volume: 3000,
  debt_tco2: 20,
  repaid_tco2: 20,
  remaining_tco2: 0,
}

const simulate = (result: apiTypes["DebtRepaymentSimulation"]) =>
  http.post("/api/tiruert/operations/simulate_debt_repayment/", () =>
    HttpResponse.json(result)
  )

const DebtRepaymentStory = (
  props: ComponentProps<typeof DebtRepaymentDialog>
) => {
  const { user } = useUser()
  return user ? <DebtRepaymentDialog {...props} /> : null
}

const meta: Meta<typeof DebtRepaymentDialog> = {
  component: DebtRepaymentDialog,
  title: "modules/accounting/pages/balances/biofuels/DebtRepaymentDialog",
  args: { balance, debt, onClose: fn() },
  render: (args) => <DebtRepaymentStory {...args} />,
  parameters: {
    msw: { handlers: [...COMMON_MOCKS, simulate(simulation)] },
  },
}

export default meta
type Story = StoryObj<typeof DebtRepaymentDialog>

const next = async (canvasElement: HTMLElement) => {
  const canvas = within(canvasElement)
  const button = await canvas.findByRole("button", { name: "Suivant" })
  await waitFor(() => expect(button).toBeEnabled())
  await userEvent.click(button)
}

export const TotalRepayment: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await next(canvasElement)
    await canvas.findByText("3 000 litres")
    await expect(
      canvas.queryByText("Nombre de lots prélevés")
    ).not.toBeInTheDocument()
    await expect(canvas.queryByRole("spinbutton")).not.toBeInTheDocument()
    await expect(canvas.getByRole("button", { name: "Suivant" })).toBeEnabled()
    await next(canvasElement)
    await canvas.findByText("Dette restant à acquitter")
  },
}

export const PartialRepayment: Story = {
  parameters: {
    msw: {
      handlers: [
        ...COMMON_MOCKS,
        simulate({
          ...simulation,
          repaid_tco2: 12,
          remaining_tco2: 8,
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await next(canvasElement)
    await canvas.findByText(/remboursement partiel/)
    await canvas.findByText("8 tCO2 évitées")
    await expect(canvas.getByRole("button", { name: "Suivant" })).toBeEnabled()
  },
}

export const RoundedRepayment: Story = {
  parameters: {
    msw: {
      handlers: [
        ...COMMON_MOCKS,
        simulate({
          ...simulation,
          debt_tco2: 20.001,
          repaid_tco2: 20.001,
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await next(canvasElement)
    await canvas.findByText("3 000 litres")
    await canvas.findByText("20,001 tCO2 évitées")
    await expect(canvas.getByRole("button", { name: "Suivant" })).toBeEnabled()
  },
}

export const NoEligibleEmissions: Story = {
  parameters: {
    msw: {
      handlers: [
        ...COMMON_MOCKS,
        simulate({
          ...simulation,
          selected_lots: [],
          total_volume: 0,
          repaid_tco2: 0,
          remaining_tco2: 20,
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await next(canvasElement)
    await canvas.findByText(/Modifiez vos filtres/)
    await expect(canvas.getByRole("button", { name: "Suivant" })).toBeDisabled()
  },
}

export const SeparateDebts: Story = {
  args: { debt: { ...debt, remaining_volume: 500 } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await expect(
      await canvas.findByRole("radio", {
        name: "Dette de volume : 500 litres",
      })
    ).toBeChecked()
    await expect(
      canvas.getByRole("radio", {
        name: "Dette en émissions évitées : 20 tCO2 évitées",
      })
    ).not.toBeChecked()
  },
}

export const SeparateDebtsTco2: Story = {
  args: { debt: { ...debt, remaining_volume: 500 } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await canvas.findByRole("radio", {
      name: "Dette de volume : 500 litres",
    })
    const tco2 = canvas.getByRole("radio", {
      name: "Dette en émissions évitées : 20 tCO2 évitées",
    })
    await userEvent.click(tco2)
    await expect(tco2).toBeChecked()
    await next(canvasElement)
    await expect(
      canvas.queryByRole("button", {
        name: "Choisir une autre dette",
      })
    ).not.toBeInTheDocument()
    await next(canvasElement)
    await canvas.findByText("3 000 litres")
  },
}

export const SeparateDebtsVolume: Story = {
  args: { debt: { ...debt, remaining_volume: 500 } },
  parameters: { msw: { handlers: [...COMMON_MOCKS, ...quantityHandlers] } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await next(canvasElement)
    await next(canvasElement)
    await fillQuantityForm(canvasElement, { quantity: "100", tC02: "25" })
    await next(canvasElement)
    await canvas.findByText("Nombre de lots prélevés")
  },
}

export const VolumeRepayment: Story = {
  args: {
    debt: { ...debt, remaining_volume: 500, remaining_tco2: 0 },
  },
  parameters: { msw: { handlers: [...COMMON_MOCKS, ...quantityHandlers] } },
  play: async ({ canvasElement }) => {
    await next(canvasElement)
    await fillQuantityForm(canvasElement, { quantity: "100", tC02: "25" })
    await next(canvasElement)
    await within(canvasElement).findByText("Nombre de lots prélevés")
  },
}

export const ConfirmRepayment: Story = {
  parameters: {
    msw: {
      handlers: [
        ...COMMON_MOCKS,
        simulate(simulation),
        http.post("/api/tiruert/operations/", async ({ request }) => {
          await expect(await request.json()).toMatchObject({
            type: "DEBT_REPAYMENT",
            debt_type: "TCO2",
            lots: simulation.selected_lots.map(({ lot_id, volume }) => ({
              id: lot_id,
              volume: Number(volume),
            })),
          })
          return HttpResponse.json([], { status: 201 })
        }),
      ],
    },
  },
  play: async (context) => {
    await TotalRepayment.play?.(context)
    await userEvent.click(
      within(context.canvasElement).getByRole("button", {
        name: "Valider l'acquittement de dette",
      })
    )
    await waitFor(() => expect(context.args.onClose).toHaveBeenCalled())
  },
}

export const FractionalStock: Story = {
  parameters: {
    msw: {
      handlers: [
        ...COMMON_MOCKS,
        http.get("/api/tiruert/operations/balance/", () =>
          HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
            results: [{ ...balance, available_balance: 1.5 }],
            count: 1,
            total_volume: 1.5,
          })
        ),
        simulate({
          ...simulation,
          selected_lots: [{ lot_id: 1, volume: "1.50" }],
          total_volume: 1.5,
          repaid_tco2: 0.001,
          remaining_tco2: 19.999,
        }),
      ],
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await setGHGRangeValue({
      canvasElement,
      cursorIndex: 0,
      value: "50",
    })
    await canvas.findByText(/1,5 litre/)
    await next(canvasElement)
    await canvas.findByText(/remboursement partiel/)
    await expect(canvas.getByRole("button", { name: "Suivant" })).toBeEnabled()
  },
}
