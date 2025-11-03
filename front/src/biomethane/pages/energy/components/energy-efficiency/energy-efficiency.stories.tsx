import type { Meta, StoryObj } from "@storybook/react"
import { EnergyEfficiency } from "./energy-efficiency"
import { contractData } from "biomethane/pages/contract/tests/contract.data"
import { energyData } from "../../tests/energy.data"
import { TariffReference } from "biomethane/pages/contract/types"
import { userEvent, waitFor, within } from "@storybook/test"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import mswHandlers from "@storybook/mocks"
import { mergeDeepRight } from "ramda"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneEnergy } from "../../types"

const meta: Meta<typeof EnergyEfficiency> = {
  title: "modules/biomethane/pages/energy/components/EnergyEfficiency",
  component: EnergyEfficiency,
  ...mergeDeepRight(AnnualDeclarationStoryUtils, {
    parameters: {
      msw: [...AnnualDeclarationStoryUtils.parameters.msw, ...mswHandlers],
    },
  }),
  decorators: [
    ...AnnualDeclarationStoryUtils.decorators,
    (Story, { args }) => {
      const form = useForm<BiomethaneEnergy | object>(args?.energy ?? {})
      return (
        <FormContext.Provider value={form}>
          <SectionsManagerProvider>
            <Story />
          </SectionsManagerProvider>
        </FormContext.Provider>
      )
    },
  ],
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
