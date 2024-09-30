import type { Preview } from "@storybook/react"
import "../src/carbure/assets/css/index.css"
import i18n from "../src/i18n"
import { I18nextProvider } from "react-i18next"
import { useEffect } from "react"

const withI18next = (Story, context) => {
  const { locale } = context.globals

  useEffect(() => {
    i18n.changeLanguage(locale)
  }, [locale])

  return (
    <I18nextProvider i18n={i18n}>
      <Story />
    </I18nextProvider>
  )
}

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
}

export const globalTypes = {
  locale: {
    name: "Locale",
    description: "Internationalization locale",
    toolbar: {
      icon: "globe",
      items: [
        { value: "fr", title: "French" },
        { value: "en", title: "English" },
      ],
      showName: true,
    },
  },
}

export const decorators = [withI18next]

export default preview
