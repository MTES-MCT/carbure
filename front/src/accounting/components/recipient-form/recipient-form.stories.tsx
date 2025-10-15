import { Meta, StoryObj } from "@storybook/react"
import { RecipientForm } from "./recipient-form"
import { Form, useForm } from "common/components/form2"
import { okFindEligibleTiruertEntities } from "./__test__/api"
import { fillRecipientForm } from "./recipient-form.stories.utils"

const meta: Meta<typeof RecipientForm> = {
  component: RecipientForm,
  title: "modules/accounting/components/RecipientForm",
  parameters: {
    msw: {
      handlers: [okFindEligibleTiruertEntities],
    },
  },
  render: (args) => {
    const form = useForm({})

    return (
      <Form form={form}>
        <RecipientForm {...args} />
      </Form>
    )
  },
}
type Story = StoryObj<typeof RecipientForm>

export default meta

export const Default: Story = {
  play: async ({ canvasElement }) => {
    await fillRecipientForm(canvasElement)
  },
}
