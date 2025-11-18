import { StoryFn } from "@storybook/react"
import { WatchedFieldsProvider } from "./watched-fields.provider"

export const generateWatchedFieldsProvider = (watchedFields: string[]) => {
  return (Story: StoryFn) => (
    <WatchedFieldsProvider
      apiFunction={() => Promise.resolve(watchedFields)}
      queryKey="contract-watched-fields"
    >
      <Story />
    </WatchedFieldsProvider>
  )
}
