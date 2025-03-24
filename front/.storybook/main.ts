import type { StorybookConfig } from "@storybook/react-vite"
import tsconfigPaths from "vite-tsconfig-paths"
const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@chromatic-com/storybook",
    "@storybook/addon-interactions",
    "storybook-addon-remix-react-router",
    "storybook-addon-mock-date",
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
