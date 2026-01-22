import type { Meta, StoryObj } from "@storybook/react"
import { EnergyTypes } from "./energy-types"
import { contractData } from "biomethane/pages/contract/tests/contract.data"
import {
  InstallationCategory,
  TariffReference,
} from "biomethane/pages/contract/types"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneEnergyInputRequest } from "biomethane/pages/energy/types"

const meta: Meta<typeof EnergyTypes> = {
  title: "modules/biomethane/pages/energy/components/EnergyTypes",
  component: EnergyTypes,
  decorators: [
    (Story) => {
      const form = useForm<Pick<BiomethaneEnergyInputRequest, "energy_types">>({
        energy_types: [],
      })
      return (
        <FormContext.Provider value={form}>
          <Story />
        </FormContext.Provider>
      )
    },
  ],
}

export default meta
type Story = StoryObj<typeof EnergyTypes>

export const Contrat2011: Story = {
  parameters: {
    docs: "Options displayed for tariff reference 2011",
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
    },
  },
}

export const Contrat2020: Story = {
  parameters: {
    docs: "Options displayed for tariff reference 2020",
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2020,
    },
  },
}

export const Contract2020WithInstallationCategory2: Story = {
  parameters: {
    docs: "Options displayed for tariff reference 2020 with installation category 2",
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2020,
      installation_category: InstallationCategory.INSTALLATION_CATEGORY_2,
    },
  },
}

export const Contrat2023: Story = {
  parameters: {
    docs: "Options displayed for tariff reference 2023",
  },
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2023,
    },
  },
}
