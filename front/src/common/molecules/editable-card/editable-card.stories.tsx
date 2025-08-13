import { Meta, StoryObj } from "@storybook/react"
import { EditableCard } from "./editable-card"
import { Button } from "common/components/button2"
import { useState } from "react"

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

/**
 * This story shows how to use the `children` prop to display a custom content.
 * The `children` prop can be a function that receives the editing state.
 *
 * For our needs, we have to pass the editing state to false when the form is completed.
 * This is why we use the `EditableCard.Form` component. It will close the editing state when the form is completed.
 *
 */
export const CustomChildren: Story = {
  args: {
    children: ({ isEditing }) => (
      <div>
        <p>isEditing: {isEditing ? "true" : "false"}</p>
        {isEditing ? (
          <EditableCard.Form
            onSubmit={() => new Promise((resolve) => setTimeout(resolve, 2000))}
          >
            <button type="submit">Valider pour fermer le formulaire</button>
          </EditableCard.Form>
        ) : (
          <p>Ouvrez le composant pour tester le comportement</p>
        )}
      </div>
    ),
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

export const ControlledEditing: Story = {
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  render: (args) => {
    const [isEditing, setIsEditing] = useState(false)

    return (
      <EditableCard {...args} isEditing={isEditing} onEdit={setIsEditing}>
        <p>isEditing: {isEditing ? "true" : "false"}</p>
        <button onClick={() => setIsEditing(!isEditing)}>
          controler l'ouverture/fermeture
        </button>
      </EditableCard>
    )
  },
  args: {
    children: null,
  },
}

export const CustomHeaderActions: Story = {
  args: {
    children: <div>children</div>,
    headerActions: <Button>Custom button</Button>,
  },
}

export const NoHeaderActions: Story = {
  args: {
    children: <div>children</div>,
    headerActions: null,
  },
}
