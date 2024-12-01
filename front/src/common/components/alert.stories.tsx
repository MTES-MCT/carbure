// Change a comment that triggers rebuild
import type { Meta, StoryObj } from "@storybook/react"

import { Alert } from "./alert"
import { SurveyLine } from "./icon"

const meta: Meta<typeof Alert> = {
  component: Alert,
  title: "legacy/Alert",
}
type Story = StoryObj<typeof Alert>

export default meta

export const AllVariants: Story = {
  render: (args) => {
    return (
      <>
        <Alert {...args} variant="info">
          <p>Info</p>
        </Alert>
        <Alert {...args} variant="success">
          <p>Success</p>
        </Alert>
        <Alert {...args} variant="warning">
          <p>Warning</p>
        </Alert>
        <Alert {...args} variant="danger">
          <p>Danger</p>
        </Alert>
      </>
    )
  },
}

export const Label: Story = {
  args: {
    label: "Label",
  },
}

export const Loading: Story = {
  args: {
    loading: true,
  },
}

export const LabelAndChildren: Story = {
  args: {
    label:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    icon: SurveyLine,
    children: <p>Children</p>,
  },
}

export const Multiline: Story = {
  args: {
    multiline: true,
    icon: SurveyLine,
    label:
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    children: <p>Children</p>,
  },
}
