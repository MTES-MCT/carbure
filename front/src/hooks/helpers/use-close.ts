import { useHistory } from "react-router-dom"

// create a shortcut function to go to the specified link
export default function useClose(to: string) {
  const history = useHistory()
  const close = () => history.push(to)
  return close
}
