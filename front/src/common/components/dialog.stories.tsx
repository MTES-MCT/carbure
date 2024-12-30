import type { Meta, StoryObj } from "@storybook/react"
import { Dialog } from "./dialog"

const meta: Meta<typeof Dialog> = {
  component: Dialog,
  title: "legacy/Dialog",
  args: {
    children: (
      <>
        <header>
          <h1>Ajout organisation</h1>
        </header>
        <main>
          <section>une section</section>
        </main>
      </>
    ),
  },
}

type Story = StoryObj<typeof Dialog>

export default meta

export const Default: Story = {}
