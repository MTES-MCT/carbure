import Select from "common/components/select"
import useLocalStorage from "common/hooks/storage"
import { useMatomo } from "matomo"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"

type Lang = "fr" | "en"

const languages = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
]

export const LanguageSelection = () => {
  const { i18n } = useTranslation()
  const matomo = useMatomo()

  const [lang, setLang] = useLocalStorage<Lang | undefined>(
    "carbure:language",
    i18n.language as Lang
  )

  useEffect(() => {
    i18n.changeLanguage(lang)
  }, [lang, i18n])

  return (
    <Select
      asideX
      variant="text"
      value={lang}
      onChange={(lang) => {
        matomo.push(["trackEvent", "menu", "change-language", lang])
        setLang(lang)
      }}
      options={languages}
    />
  )
}
