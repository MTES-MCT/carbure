import { Select, SelectProps } from "common/components/selects2"
import useLocalStorage from "common/hooks/storage"
import { useMatomo } from "matomo"
import { useTranslation } from "react-i18next"

type Lang = "fr" | "en"

const languages = [
  { value: "fr", label: "🇫🇷 Français", displayedValue: "🇫🇷" },
  { value: "en", label: "🇬🇧 English", displayedValue: "🇬🇧" },
]

// type LanguageSelectorProps = {
//   size?: SelectProps<{ value: Lang; displayedValue: string }, Lang>[""]
// }

export const LanguageSelector = () => {
  const { i18n } = useTranslation()
  const matomo = useMatomo()

  const [lang, setLang] = useLocalStorage<Lang | undefined>(
    "carbure:language",
    i18n.language as Lang
  )

  return (
    <Select
      options={languages}
      value={lang}
      onChange={(lang) => {
        matomo.push(["trackEvent", "menu", "change-language", lang])
        setLang(lang)
        i18n.changeLanguage(lang)
      }}
      valueRenderer={(item) => item.displayedValue}
      size="small"
    />
  )
}
