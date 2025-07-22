import type { StorybookConfig } from "@storybook/react-vite"
import tsconfigPaths from "vite-tsconfig-paths"
const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@chromatic-com/storybook",
    "storybook-addon-remix-react-router",
    "storybook-addon-mock-date",
    "@storybook/addon-docs"
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },

  viteFinal: async (config) => {
    config.plugins = [...(config.plugins ?? []), tsconfigPaths()]
    return {
      ...config,
    }
  },
}
export default config
