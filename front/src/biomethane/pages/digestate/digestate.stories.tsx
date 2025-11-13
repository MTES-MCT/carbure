import { BiomethanePageHeader } from "biomethane/layouts/page-header"
import { Digestate } from "./digestate"
import { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { ContractProductionUnitProvider } from "biomethane/providers/contract-production-unit"
import { handlers as contractProductionUnitHandlers } from "biomethane/providers/contract-production-unit/contract-production-unit.stories.utils"
import { buildCurrentAnnualDeclarationHandler } from "biomethane/tests/api"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import GLOBAL_MOCKS from "@storybook/mocks"

const MOCKS = [
  ...GLOBAL_MOCKS,
  ...AnnualDeclarationStoryUtils.parameters.msw.handlers,
  ...contractProductionUnitHandlers,
]

const getAnnualDeclarationHandler = (year: number) =>
  buildCurrentAnnualDeclarationHandler({
    year,
    missing_fields: {
      digestate_missing_fields: ["raw_digestate_tonnage_produced"],
    },
    is_complete: false,
  })

const meta: Meta<typeof Digestate> = {
  title: "modules/biomethane/pages/Digestate",
  component: Digestate,
  parameters: {
    ...AnnualDeclarationStoryUtils.parameters,
    msw: {
      handlers: MOCKS,
    },
  },
  decorators: [
    (Story) => (
      <ContractProductionUnitProvider>
        <BiomethanePageHeader>
          <Story />
        </BiomethanePageHeader>
      </ContractProductionUnitProvider>
    ),
    ...AnnualDeclarationStoryUtils.decorators,
  ],
}

export default meta
type Story = StoryObj<typeof Digestate>

export const DoNotShowMissingFieldsWhenHashIsPresentIfTheDeclarationIsNotEditable: Story =
  {
    parameters: {
      msw: {
        handlers: [getAnnualDeclarationHandler(2024), ...MOCKS],
      },
      reactRouter: reactRouterParameters({
        location: {
          hash: "#missing-fields",
          pathParams: {
            year: "2025",
          },
          path: "/:year/digestate",
        },
        routing: {
          path: "/:year/digestate",
          handle: "Digestate",
        },
      }),
    },
  }

export const ShowMissingFieldsWhenHashIsPresentIfTheDeclarationIsEditable: Story =
  {
    ...DoNotShowMissingFieldsWhenHashIsPresentIfTheDeclarationIsNotEditable,
    parameters: {
      ...DoNotShowMissingFieldsWhenHashIsPresentIfTheDeclarationIsNotEditable.parameters,
      msw: {
        handlers: [getAnnualDeclarationHandler(2025), ...MOCKS],
      },
    },
  }
