import type { Meta, StoryObj } from "@storybook/react"
import { Dialog } from "./dialog"

const meta: Meta<typeof Dialog> = {
  component: Dialog,
  title: "common/components/Dialog",
  args: {
    header: (
      <>
        <Dialog.Title>Ajout organisation</Dialog.Title>
        <Dialog.Description>
          Ajouter une organisation à votre compte
        </Dialog.Description>
      </>
    ),
    children: <>une section</>,
  },
}

type Story = StoryObj<typeof Dialog>

export default meta

export const Default: Story = {}
