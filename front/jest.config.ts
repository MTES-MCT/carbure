import type { Config } from "jest"

const config: Config = {
  roots: ["<rootDir>/src"],
  modulePaths: ["<rootDir>/src"],
  testEnvironment: "jsdom",
  transform: {
    ".(ts|tsx)": "ts-jest",
    // ".(json|css)": "babel-jest",
  },
  testMatch: ["**/__test__/**/*.spec.ts?(x)"],
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.tsx"],
  moduleNameMapper: {
    "^.+\\.(css|sass|scss)$": "identity-obj-proxy", // Si tu utilises des CSS modules
    "^.+\\.svg$": "jest-transformer-svg",
  },
  transformIgnorePatterns: [
    "node_modules/(?!(axios|leaflet-defaulticon-compatibility))/",
    "[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs|cjs|ts|tsx|json)$",
    "^.+\\.module\\.(css|sass|scss)$",
    "^.+\\.json$",
  ],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  setupFiles: ["./jest.polyfills.js"],
  testEnvironmentOptions: {
    customExportConditions: [""],
  },
}

export default config
