module.exports = {
  roots: ["<rootDir>/src"],
  modulePaths: ["<rootDir>/src"],
  testEnvironment: "jsdom",
  transform: {
    ".(ts|tsx)": "ts-jest",
  },
  testMatch: ["**/__test__/**/*.spec.ts?(x)"],
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.tsx"],
  moduleNameMapper: {
    "^.+\\.module\\.(css|sass|scss)$": "identity-obj-proxy", // Si tu utilises des CSS modules
  },
  transformIgnorePatterns: [
    "node_modules/(?!axios)/",
    "[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs|cjs|ts|tsx|json)$",
    "^.+\\.module\\.(css|sass|scss)$",
  ],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  setupFiles: ["./jest.polyfills.js"],
  testEnvironmentOptions: {
    customExportConditions: [""],
  },
}
