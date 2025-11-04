import { Meta, StoryObj } from "@storybook/react"
import { BiomethanePageHeader } from "./page-header"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { getAnnualDeclarationYearsOk } from "biomethane/tests/api"
import GLOBAL_MOCKS from "@storybook/mocks"
import { mockUser } from "common/__test__/helpers"
import { EntityType, UserRole } from "common/types"

const MOCKS = [
  GLOBAL_MOCKS,
  getAnnualDeclarationYearsOk,
  ...AnnualDeclarationStoryUtils.parameters.msw.handlers,
]
const meta: Meta<typeof BiomethanePageHeader> = {
  title: "modules/biomethane/layouts/BiomethanePageHeader",
  component: BiomethanePageHeader,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    ...AnnualDeclarationStoryUtils.parameters,
    msw: {
      handlers: MOCKS,
    },
  },
  args: {
    children: <div>this is the content of the page</div>,
  },
}

export default meta
type Story = StoryObj<typeof BiomethanePageHeader>

// If the current year is 2025, a notice with a button to validate the declaration should be displayed
export const DefaultLayoutForTheCurrentYear: Story = {}

export const DefaultLayoutForTheCurrentYearWithReadOnlyPermissions: Story = {
  parameters: {
    msw: {
      handlers: [
        mockUser(EntityType.Producteur_de_biom_thane, {
          right: {
            role: UserRole.ReadOnly,
          },
        }),
        ...MOCKS,
      ],
    },
  },
}
