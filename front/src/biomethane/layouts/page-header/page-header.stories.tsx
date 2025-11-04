import { Meta, StoryObj } from "@storybook/react"
import { BiomethanePageHeader } from "./page-header"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import {
  buildCurrentAnnualDeclarationHandler,
  getAnnualDeclarationYearsOk,
} from "biomethane/tests/api"
import GLOBAL_MOCKS from "@storybook/mocks"
import { mockUser } from "common/__test__/helpers"
import { EntityType, UserRole } from "common/types"
import { AnnualDeclarationStatus } from "biomethane/types"
import { userEvent, waitFor, within } from "@storybook/test"

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

// If the current year is 2025, but the user is read only, he can't validate the declaration
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

export const LayoutForTheCurrentYearWhenTheDeclarationIsValidated: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          status: AnnualDeclarationStatus.DECLARED,
        }),
        ...MOCKS,
      ],
    },
  },
}

export const LayoutForThePreviousYear: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          status: AnnualDeclarationStatus.DECLARED,
          year: 2024,
        }),
        ...MOCKS,
      ],
    },
  },
}

export const DisplayValidateDeclarationDialogIfTheDeclarationIsComplete: Story =
  {
    play: async ({ canvasElement }) => {
      const { getByRole } = within(canvasElement)
      const button = await waitFor(() =>
        getByRole("button", { name: "Transmettre mes informations annuelles" })
      )

      await userEvent.click(button)
    },
  }

export const DisplayMissingFieldsDialogIfTheDeclarationIsNotComplete: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          is_complete: false,
        }),
        ...MOCKS,
      ],
    },
  },
  play: DisplayValidateDeclarationDialogIfTheDeclarationIsComplete.play,
}
