import type { Meta, StoryObj } from "@storybook/react"

import { FromDepotForm } from "./from-depot-form"
import { Form, useForm } from "common/components/form2"
import { FromDepotFormProps } from "./from-depot-form.types"
import { okGetDeliverySites } from "common/__test__/api"
import { fillFromDepotForm } from "./from-depot-form.stories.utils"

const meta: Meta<typeof FromDepotForm> = {
  component: FromDepotForm,
  title: "modules/accounting/components/FromDepotForm",
  parameters: {
    msw: {
      handlers: [okGetDeliverySites],
    },
  },
  render: () => {
    const form = useForm<FromDepotFormProps>({})

    return (
      <Form form={form}>
        <FromDepotForm />
      </Form>
    )
  },
}
type Story = StoryObj<typeof FromDepotForm>

export default meta

export const SelectDepot: Story = {
  play: async ({ canvasElement }) => {
    await fillFromDepotForm(canvasElement)
  },
}
