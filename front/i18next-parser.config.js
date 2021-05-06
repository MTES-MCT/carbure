module.exports = {
  input: ["./src/**/*.{ts,tsx}", "!./src/**/__test__/**"],
  output: "public/locales/$LOCALE/$NAMESPACE.json",
  locales: ["fr", "en"],
  keySeparator: false,
  nsSeparator: false,
  verbose: true,
  useKeysAsDefaultValue: true,
}
