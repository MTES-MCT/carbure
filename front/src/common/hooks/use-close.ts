import { useNavigate } from "react-router-dom"

// create a shortcut function to go to the specified link
export default function useClose(to: string) {
  const navigate = useNavigate()
  return () => navigate(to)
}
