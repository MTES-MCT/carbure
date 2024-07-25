import { useEffect } from "react"

export default function useTitle(title: string, prefix = "CarbuRe ∙ ") {
  useEffect(() => {
    document.title = `${prefix}${title}`
  }, [prefix, title])
}
