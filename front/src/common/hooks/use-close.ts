import { useRelativePush } from "../components/relative-route"

// create a shortcut function to go to the specified link
export default function useClose(to: string) {
  const push = useRelativePush()
  return () => push(to)
}
