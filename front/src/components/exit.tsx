import { useEffect } from "react"

// exit the current react app and go to the given url
const Exit = ({ to }: { to: string }) => {
  useEffect(() => {
    window.location.pathname = to
  }, [])

  return null
}

export default Exit
