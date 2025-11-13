import type { Meta, StoryObj } from "@storybook/react"

import { QuantityForm } from "./quantity-form"
import { Form, useForm } from "common/components/form2"
import { CreateOperationType } from "accounting/types"
import { balance } from "accounting/__test__/data/balances"
import { userEvent, waitFor, within } from "@storybook/test"
import {
  okSimulateMinMaxWithEqualValues,
  okSimulateMinMaxWithZeroValues,
} from "accounting/__test__/api/biofuels/operations"
import { baseHandlers } from "./quantity-form.stories.utils"
import { getViewport } from "@storybook/mocks/utils"

const meta: Meta<typeof QuantityForm> = {
  component: QuantityForm,
  title: "modules/accounting/components/QuantityForm",
  args: {
    balance,
    type: CreateOperationType.TRANSFERT,
    quantityMax: 10000,
  },
  parameters: {
    msw: {
      handlers: baseHandlers,
    },
  },
  render: (args) => {
    const form = useForm({})

    return (
      <Form form={form}>
        <QuantityForm {...args} />
      </Form>
    )
  },
}
type Story = StoryObj<typeof QuantityForm>

export default meta

export const DefaultQuantityForm: Story = {}

export const ValidateQuantityButtonEnabled: Story = {
  parameters: {
    docs: {
      description:
        "Set a value in the quantity input and the validate button should be enabled",
    },
  },
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const input = await waitFor(() => getByRole("spinbutton"))

    await userEvent.type(input, "1000")
  },
}

export const ShowErrorWhenQuantityIsGreaterThanQuantityMax: Story = {
  parameters: {
    docs: {
      description:
        "Display an error when the quantity is greater than the quantity max available",
    },
  },
  args: {
    quantityMax: 100,
  },
  play: async (props) => {
    await ValidateQuantityButtonEnabled.play?.(props)

    const { getByRole } = within(props.canvasElement)
    const button = await waitFor(() =>
      getByRole("button", { name: "Valider la quantité" })
    )

    await userEvent.click(button)
  },
}

export const ShowErrorWhenSimulateMinMaxReturnsZeroValues: Story = {
  parameters: {
    docs: {
      description:
        "Show an error when the simulate min max returns zero values",
    },
    msw: {
      handlers: [okSimulateMinMaxWithZeroValues, ...baseHandlers],
    },
  },
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
}

export const DisplayAvoidedEmissionsWhenQuantityIsDeclared: Story = {
  parameters: {
    docs: {
      description:
        "Display the avoided emissions component with the range returned by the backend when the quantity is declared",
    },
  },
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
}

export const FocusOnAvoidedEmissionsWhenQuantityIsDeclared: Story = {
  parameters: {
    docs: {
      description:
        "Focus on the avoided emissions input when the quantity is declared (visible when the viewport height is small)",
    },
    viewport: getViewport("fullModal", { width: "1200px", height: "200px" }),
  },
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
}

export const DisplayAvoidedEmissionsWhenQuantityIsDeclaredWithEqualValues: Story =
  {
    parameters: {
      docs: {
        description:
          "Display the avoided emissions component with the range returned by the backend when the quantity is declared with equal values",
      },
      msw: {
        // Overrides the simulate min max mock api by setting the needed mock as first
        handlers: [okSimulateMinMaxWithEqualValues, ...baseHandlers],
      },
    },
    play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
  }

export const ResetQuantityDeclared: Story = {
  parameters: {
    docs: {
      description:
        "When the quantity is declared, the button should be replaced by a reset button that hides the avoided emissions component",
    },
  },
  play: async (props) => {
    const { getByRole } = within(props.canvasElement)
    await ShowErrorWhenQuantityIsGreaterThanQuantityMax.play?.(props)

    const button = await waitFor(() =>
      getByRole("button", { name: "Modifier" })
    )

    await userEvent.click(button)
  },
}
