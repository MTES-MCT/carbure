import type { Meta, StoryObj } from "@storybook/react"
import { MissingFields, MissingFieldsProps } from "./missing-fields"
import { AnnualDeclarationStoryUtils } from "biomethane/providers/annual-declaration/annual-declaration.stories.utils"
import { buildCurrentAnnualDeclarationHandler } from "biomethane/tests/api"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

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
  args: {
    onPageClick: fn(),
  },
}

export default meta
type Story = StoryObj<typeof MissingFields>

// Displays when there are no missing fields.
export const NoMissingFields: Story = {
  parameters: {
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

// Shows missing fields only for digestate.
export const DisplayOnlyDigestateMissingFields: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: ["digestate_field_1"],
            energy_missing_fields: [],
          },
        }),
      ],
    },
  },
  play: async ({ canvasElement, args }) => {
    await clickOnLink(canvasElement, "Digestat", args.onPageClick)
  },
}

// Shows missing fields only for energy.
export const DisplayOnlyEnergyMissingFields: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: [],
            energy_missing_fields: ["energy_field_1"],
          },
        }),
      ],
    },
  },
  play: async ({ canvasElement, args }) => {
    await clickOnLink(canvasElement, "Energie", args.onPageClick)
  },
}

// Displays missing fields for both energy and digestate.
export const DisplayBothEnergyAndDigestateMissingFields: Story = {
  parameters: {
    msw: {
      handlers: [
        buildCurrentAnnualDeclarationHandler({
          missing_fields: {
            digestate_missing_fields: ["digestate_field_1"],
            energy_missing_fields: ["energy_field_1"],
          },
        }),
      ],
    },
  },
}

export const DisplayNothingWhenTheDeclarationIsNotEditable: Story = {
  parameters: {
    mockingDate: new Date(2024, 11, 1),
  },
  play: NoMissingFields.play,
}
