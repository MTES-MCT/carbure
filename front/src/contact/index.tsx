import { usePrivateNavigation } from "common/layouts/navigation"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"

declare global {
  interface Window {
    Tally: {
      loadEmbeds: () => void
    }
  }
}

export const ContactPage = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Contact"))
  // The code below will load the embed
  useEffect(() => {
    const widgetScriptSrc = "https://tally.so/widgets/embed.js"

    const load = () => {
      // Load Tally embeds
      if (typeof window.Tally !== "undefined") {
        window.Tally.loadEmbeds()
        return
      }

      // Fallback if window.Tally is not available
      document
        .querySelectorAll("iframe[data-tally-src]:not([src])")
        .forEach((iframeEl) => {
          if (iframeEl instanceof HTMLIFrameElement) {
            iframeEl.src = iframeEl.dataset.tallySrc ?? ""
          }
        })
    }

    // If Tally is already loaded, load the embeds
    if (typeof window.Tally !== "undefined") {
      load()
      return
    }

    // If the Tally widget script is not loaded yet, load it
    if (document.querySelector(`script[src="${widgetScriptSrc}"]`) === null) {
      const script = document.createElement("script")
      script.src = widgetScriptSrc
      script.onload = load
      script.onerror = load
      document.body.appendChild(script)
      return
    }
  }, [])

  return (
    <iframe
      data-tally-src="https://tally.so/embed/wodQbN?&dynamicHeight=1"
      loading="lazy"
      width="100%"
      height="100%"
    ></iframe>
  )
}
