import type { Meta, StoryObj } from "@storybook/react-vite"

import { EditableCard } from "./editable-card"
import { Button } from "common/components/button2"

const meta = {
  component: EditableCard,
  args: {
    title: "Title for an editable card",
    description: "Description for an editable card",
  },
} satisfies Meta<typeof EditableCard>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    children: <div>children</div>,
  },
}

export const CustomChildren: Story = {
  args: {
    children: ({ isEditing, setIsEditing }) => (
      <div>
        <p>isEditing: {isEditing ? "true" : "false"}</p>
        <button onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? "Stop editing" : "Start editing"}
        </button>
      </div>
    ),
  },
}

export const CustomHeaderActions: Story = {
  args: {
    children: <div>children</div>,
    headerActions: <Button>Custom button</Button>,
  },
}
