import type { Meta, StoryObj } from "@storybook/react"
import { Form, useForm } from "./form"
import { TextInput } from "../inputs2"
import { Button } from "../button2"
import { fn } from "@storybook/test"

const meta: Meta<typeof Form> = {
  component: Form,
  title: "common/components/form/Form",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  render: (args) => {
    const { bind } = useForm({
      email: "" as string | undefined,
    })
    return (
      <Form {...args} onSubmit={args.onSubmit}>
        <TextInput {...bind("email")} label="Email" required />
        <Button type="submit">Submit</Button>
      </Form>
    )
  },
  args: {
    onSubmit: fn(),
  },
}

type Story = StoryObj<typeof Form>

export default meta

export const Default: Story = {}

export const WithErrors: Story = {
  render: (args) => {
    const { bind } = useForm(
      {
        email: "" as string | undefined,
      },
      {
        errors: {
          email: "Le champ est obligatoire",
        },
      }
    )

    return (
      <Form {...args} onSubmit={args.onSubmit}>
        <TextInput {...bind("email")} label="Email" required />
        <Button type="submit">Submit</Button>
      </Form>
    )
  },
}

export const WithErrorMessage: Story = {
  render: (args) => {
    const { bind } = useForm(
      {
        email: "" as string | undefined,
      },
      {
        errors: {
          email: "Le champ est obligatoire",
        },
      }
    )

    return (
      <Form {...args} onSubmit={args.onSubmit}>
        <TextInput
          {...bind("email", { showError: true })}
          label="Email"
          required
        />
        <Button type="submit">Submit</Button>
      </Form>
    )
  },
}
