import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import Backend from "i18next-http-backend"

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    ns: [
      "translation",
      "errors",
      "errors-api",
      "fields",
      "feedstocks",
      "biofuels",
      "countries",
    ],
    supportedLngs: ["fr", "en"],
    fallbackLng: "fr",
    keySeparator: false,
    nsSeparator: false,
    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
    },
    react: {
      useSuspense: true,
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ["b", "i"],
    },
    backend: {
      loadPath: "/locales/{{lng}}/{{ns}}.json",
    },
  })

// tell TS that the i18next.t() function will never return null
declare module "i18next" {
  interface CustomTypeOptions {
    returnNull: false
  }
}

export default i18n
