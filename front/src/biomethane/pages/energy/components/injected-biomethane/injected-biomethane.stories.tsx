import type { Meta, StoryObj } from "@storybook/react"
import { InjectedBiomethane } from "./injected-biomethane"
import { contractData } from "biomethane/pages/contract/tests/contract.data"
import { energyData } from "../../tests/energy.data"
import { TariffReference } from "biomethane/pages/contract/types"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import mswHandlers from "@storybook/mocks"
import { mergeDeepRight } from "ramda"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { FormContext, useForm } from "common/components/form2"
import { BiomethaneEnergy, BiomethaneEnergyMonthlyReport } from "../../types"

const meta: Meta<typeof InjectedBiomethane> = {
  title: "modules/biomethane/pages/energy/components/InjectedBiomethane",
  component: InjectedBiomethane,
  ...mergeDeepRight(AnnualDeclarationStoryUtils, {
    parameters: {
      msw: {
        handlers: [
          ...AnnualDeclarationStoryUtils.parameters.msw.handlers,
          ...mswHandlers,
        ],
      },
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
type Story = StoryObj<typeof InjectedBiomethane>

// Test data for monthly reports (contracts 2011/2020)
// Example with 12 months for a complete calculation
// Sum = injected_volume_nm3 / average_monthly_flow_nm3_per_hour = 1 * 12 months = 12
const monthlyReports2011: BiomethaneEnergyMonthlyReport[] = Array.from(
  { length: 12 },
  (_, index) => ({
    month: index + 1,
    injected_volume_nm3: 10,
    average_monthly_flow_nm3_per_hour: 10,
    energy: 1,
  })
)

export const WithContract2011: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2011,
      cmax: 500,
    },
    energy: {
      ...energyData,
      monthly_reports: monthlyReports2011,
    },
  },
  parameters: {
    docs: {
      description:
        "Contrat 2011 : Le calcul utilise la formule '8760 * Quantité injectée (Nm3/an) / (somme heures d'injection * Cmax)'. Le champ Nm3/an est visible.",
    },
  },
}

export const WithContract2020: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2020,
      cmax: 300,
    },
    energy: {
      ...energyData,
      monthly_reports: monthlyReports2011,
    },
  },
  parameters: {
    docs: {
      description:
        "Contrat 2020 : Même formule que 2011. Le calcul nécessite les monthly_reports pour calculer la somme des heures d'injection.",
    },
  },
}

export const WithContract2021: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2021,
      pap_contracted: 10,
    },
    energy: {
      ...energyData,
      injected_biomethane_gwh_pcs_per_year: 8,
    },
  },
  parameters: {
    docs: {
      description:
        "Contrat 2021 : Le calcul utilise la formule '8760 * Quantité injectée (GWh PCS/an) / PAP du contrat'. Le champ Nm3/an n'est pas visible.",
    },
  },
}

export const WithContract2023: Story = {
  args: {
    contract: {
      ...contractData,
      tariff_reference: TariffReference.Value2023,
      pap_contracted: 10,
    },
    energy: {
      ...energyData,
      injected_biomethane_gwh_pcs_per_year: 1.2,
    },
  },
  parameters: {
    docs: {
      description:
        "Contrat 2023 : Même formule que 2021. Le champ 'Nombre d'heures de fonctionnement' est calculé et affiché automatiquement.",
    },
  },
}
