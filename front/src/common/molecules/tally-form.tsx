import { useEffect } from "react"

declare global {
  interface Window {
    Tally: {
      loadEmbeds: () => void
    }
  }
}

type TallyFormProps = {
  url: string
}

export const TallyForm = ({ url }: TallyFormProps) => {
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
      data-tally-src={url}
      loading="lazy"
      style={{
        // We need to add the margin to the iframe to avoid the border of the iframe to be cut
        margin: `calc(var(--spacing-l) * -1)`,
        height: "calc(100% + (var(--spacing-l) * 2) - 5px)",
        width: "calc(100% + (var(--spacing-l) * 2))",
      }}
    ></iframe>
  )
}
