import type { Meta, StoryObj } from "@storybook/react"
import { LanguageSelector } from "./language-selector"

const meta: Meta<typeof LanguageSelector> = {
  component: LanguageSelector,
  title: "common/molecules/LanguageSelector",
}

type Story = StoryObj<typeof LanguageSelector>

export default meta

export const Default: Story = {
  render: () => (
    <div style={{ width: "80px" }}>
      <LanguageSelector />
    </div>
  ),
}
