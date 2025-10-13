import type { Meta, StoryObj } from "@storybook/react"
import { EnergyEfficiency } from "./energy-efficiency"
import { contractData } from "biomethane/pages/contract/tests/contract.data"
import { energyData } from "../../tests/energy.data"
import { TariffReference } from "biomethane/pages/contract/types"
import { EnergyProvider } from "../../energy.hooks"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof EnergyEfficiency> = {
  title: "modules/biomethane/pages/energy/components/EnergyEfficiency",
  component: EnergyEfficiency,
  render: (args) => (
    <EnergyProvider year={2025}>
      <EnergyEfficiency {...args} />
    </EnergyProvider>
  ),
}

export default meta
type Story = StoryObj<typeof EnergyEfficiency>

export const Default: Story = {
  args: {
    contract: contractData,
  },
}

export const With2023Tariff: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2023,
    },
  },
}

export const WithErrors2023Tariff: Story = {
  args: {
    energy: {
      ...energyData,
      total_unit_electric_consumption_kwe: 2,
      injected_biomethane_gwh_pcs_per_year: 1,
    },
    contract: { ...contractData, tariff_reference: TariffReference.Value2023 },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = await waitFor(() =>
      canvas.getByRole("button", { name: "Modifier" })
    )
    await userEvent.click(button)
  },
}

export const WithErrorsNot2023Tariff: Story = {
  args: {
    energy: {
      ...energyData,
      purified_biogas_quantity_nm3: 1,
      purification_electric_consumption_kwe: 2,
    },
    contract: { ...contractData, tariff_reference: TariffReference.Value2021 },
  },
  play: WithErrors2023Tariff.play,
}
