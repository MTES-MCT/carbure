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
import { reactRouterParameters } from "storybook-addon-remix-react-router"

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

export const DefaultLayoutForTheCurrentYear: Story = {
  parameters: {
    docs: {
      description:
        "If the current year is 2025, a notice with a button to validate the declaration should be displayed",
    },
  },
}

export const DefaultLayoutForTheCurrentYearWithReadOnlyPermissions: Story = {
  parameters: {
    docs: {
      description:
        "If the current year is 2025, but the user is read only, he can't validate the declaration",
    },
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
    docs: {
      description:
        "If the selected year is 2025 and the declaration is validated, a notice with a button to correct the declaration should be displayed",
    },
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

export const ValidateThePreviousYearDeclaration: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          year: 2024,
        }),
        ...MOCKS,
      ],
    },
    docs: {
      description:
        "If the selected year is 2024 (but not the current year) and the declaration is open, the user is authorized to validated a previous declaration",
    },
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { year: "2024" },
        path: "/:year",
      },
      routing: {
        path: "/:year",
      },
    }),
  },
}

export const CouldNotValidateThePreviousYearDeclaration: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          year: 2024,
          is_open: false,
        }),
        ...MOCKS,
      ],
    },
    docs: {
      description:
        "If the selected year is 2024 and the declaration is not open and the current declaration is 2026, the user just can see the declaration as read only",
    },
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { year: "2024" },
        path: "/:year",
      },
      routing: {
        path: "/:year",
      },
    }),
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

export const DisplayValidateDeclarationDialogIfTheDeclarationIsCompleteWhenSelectedYearIsNotTheCurrentYear: Story =
  {
    parameters: {
      msw: {
        handlers: [
          buildCurrentAnnualDeclarationHandler({
            year: 2024,
            status: AnnualDeclarationStatus.OVERDUE,
          }),
          ...MOCKS,
        ],
      },
      docs: {
        description:
          "If the selected year is 2024 (but not the current year) and the declaration is overdue, the user is authorized to validated a previous declaration with a specific message",
      },
      reactRouter: reactRouterParameters({
        location: {
          pathParams: { year: "2024" },
          path: "/:year",
        },
        routing: {
          path: "/:year",
        },
      }),
    },
    play: DisplayValidateDeclarationDialogIfTheDeclarationIsComplete.play,
  }

export const DisplayMissingFieldsDialogIfTheDeclarationIsNotComplete: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          is_complete: false,
          missing_fields: {
            digestate_missing_fields: ["digestate_missing_field_1"],
            energy_missing_fields: [
              "energy_missing_field_1",
              "energy_missing_field_2",
            ],
          },
        }),
        ...MOCKS,
      ],
    },
  },
  play: DisplayValidateDeclarationDialogIfTheDeclarationIsComplete.play,
}

export const DisplayOverdueDeclarationNoticeIfTheDeclarationIsOverdue: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          status: AnnualDeclarationStatus.OVERDUE,
        }),
        ...MOCKS,
      ],
    },
  },
}
