import type { Meta, StoryObj } from "@storybook/react"
import { MissingFields, MissingFieldsProps } from "./missing-fields"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import {
  buildCurrentAnnualDeclarationHandler,
  getCurrentAnnualDeclarationOk,
} from "biomethane/tests/api"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import GLOBAL_MOCKS from "@storybook/mocks"

const MOCKS = [...GLOBAL_MOCKS, getCurrentAnnualDeclarationOk]
const clickOnLink = async (
  canvasElement: HTMLElement,
  linkName: string,
  onPageClick: MissingFieldsProps["onPageClick"]
) => {
  const canvas = within(canvasElement)
  const link = await waitFor(() => canvas.getByRole("link", { name: linkName }))
  // Prevent actual navigation in Storybook to assert on onPageClick
  link.addEventListener("click", (e) => e.preventDefault())

  await userEvent.click(link)

  await waitFor(() => expect(onPageClick).toHaveBeenCalledWith(linkName))
}
const meta: Meta<typeof MissingFields> = {
  title: "modules/biomethane/components/MissingFields",
  component: MissingFields,
  ...AnnualDeclarationStoryUtils,
  parameters: {
    msw: {
      handlers: MOCKS,
    },
  },
  args: {
    onPageClick: fn(),
  },
}

export default meta
type Story = StoryObj<typeof MissingFields>

export const NoMissingFields: Story = {
  parameters: {
    docs: {
      description: "Displays when there are no missing fields.",
    },
    chromatic: { disableSnapshot: true },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const notice = await waitFor(() =>
      canvas.queryByTestId("missing-fields-notice")
    )
    await expect(notice).toBeNull()
  },
}

export const DisplayOnlyDigestateMissingFields: Story = {
  parameters: {
    docs: {
      description: "Shows missing fields only for digestate.",
    },
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: ["digestate_field_1"],
            energy_missing_fields: [],
          },
        }),
        ...MOCKS,
      ],
    },
  },
  play: async ({ canvasElement, args }) => {
    await clickOnLink(canvasElement, "Digestat", args.onPageClick)
  },
}

export const DisplayOnlyEnergyMissingFields: Story = {
  parameters: {
    docs: {
      description: "Shows missing fields only for energy.",
    },
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: [],
            energy_missing_fields: ["energy_field_1"],
          },
        }),
        ...MOCKS,
      ],
    },
  },
  play: async ({ canvasElement, args }) => {
    await clickOnLink(canvasElement, "Energie", args.onPageClick)
  },
}

export const DisplayBothEnergyAndDigestateMissingFields: Story = {
  parameters: {
    docs: {
      description: "Displays missing fields for both energy and digestate.",
    },
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: ["digestate_field_1"],
            energy_missing_fields: ["energy_field_1"],
          },
        }),
        ...MOCKS,
      ],
    },
  },
}

export const DisplayNothingWhenTheDeclarationIsNotEditable: Story = {
  parameters: {
    mockingDate: new Date(2024, 11, 1),
    docs: {
      description: "Displays nothing when the declaration is not editable.",
    },
    chromatic: { disableSnapshot: true },
  },
  play: NoMissingFields.play,
}
