import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import Backend from "i18next-http-backend"
import LanguageDetector from "i18next-browser-languagedetector"

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    ns: [
      "translation",
      "errors",
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
    },
    backend: {
      loadPath: "/v2/locales/{{lng}}/{{ns}}.json",
    },
  })

export default i18n
