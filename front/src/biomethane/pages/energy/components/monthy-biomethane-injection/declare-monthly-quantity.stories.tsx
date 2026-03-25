import type { Meta, StoryObj } from "@storybook/react"
import { userEvent, waitFor, within } from "@storybook/test"
import mswHandlers from "@storybook/mocks"
import { mockUser } from "common/__test__/helpers"
import { EntityType } from "common/types"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { DeclareMonthlyQuantity } from "./declare-monthly-quantity"
import type { BiomethaneEnergyMonthlyReport } from "../../types"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import { getViewport } from "@storybook/mocks/utils"

const year = 2025

const buildMonthlyReports = (
  hoursDelta: number
): BiomethaneEnergyMonthlyReport[] =>
  Array.from({ length: 12 }, (_, index) => {
    const month = index + 1
    const hoursInMonth = new Date(year, month, 0).getDate() * 24

    // On force la formule heures = volume / débit à être :
    // injectionHours = hoursInMonth + hoursDelta
    return {
      month,
      injected_volume_nm3: hoursInMonth + hoursDelta,
      average_monthly_flow_nm3_per_hour: 1,
      energy: 1,
    }
  })

const meta: Meta<typeof DeclareMonthlyQuantity> = {
  title:
    "modules/biomethane/pages/energy/components/monthy-biomethane-injection/DeclareMonthlyQuantity",
  component: DeclareMonthlyQuantity,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    viewport: getViewport("fullModal", { width: "1200px", height: "1100px" }),
    mockingDate: new Date(year, 2, 1),
    msw: {
      handlers: [
        mockUser(EntityType.Producteur_de_biom_thane),
        ...(AnnualDeclarationStoryUtils.parameters?.msw?.handlers ?? []),
        ...mswHandlers,
      ],
    },
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { year: "2025" },
        path: "/:year",
      },
      routing: {
        path: "/:year",
      },
    }),
  },
  args: {
    isReadOnly: false,
    monthlyReports: [],
  },
}

export default meta
type Story = StoryObj<typeof DeclareMonthlyQuantity>

export const NominalMonthlyReportsEmpty: Story = {
  args: {
    monthlyReports: [],
  },
}

export const ValidMonthlyReports: Story = {
  args: {
    monthlyReports: buildMonthlyReports(-10),
  },
}

export const InvalidMonthlyReports: Story = {
  args: {
    monthlyReports: buildMonthlyReports(10),
  },
}

export const InvalidMonthlyReportsClickValidate: Story = {
  args: {
    monthlyReports: buildMonthlyReports(10),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    const button = await waitFor(() =>
      canvas.getByRole("button", { name: /Enregistrer/i })
    )

    await userEvent.click(button)

    // Le composant bloque l'enregistrement et affiche une notification
    const body = within(canvasElement.ownerDocument.body)
    await waitFor(() =>
      body.getByText(
        "Les heures d'injection calculées sont supérieures au nombre d'heures du mois :"
      )
    )
  },
}
