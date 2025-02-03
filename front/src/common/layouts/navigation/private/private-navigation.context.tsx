import {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

interface PrivateNavigationContext {
  title: string
  setTitle: (title: string) => void
}
export const PrivateNavigationContext = createContext<PrivateNavigationContext>(
  {
    title: "",
    setTitle: (title) => title,
  }
)

export const usePrivateNavigation = (newTitle: string) => {
  const { setTitle } = useContext(PrivateNavigationContext)

  useEffect(() => {
    setTitle(newTitle)
  }, [newTitle, setTitle])
}

export const PrivateNavigationProvider = ({ children }: PropsWithChildren) => {
  const [title, setTitle] = useState("")

  const value = useMemo(
    () => ({
      title,
      setTitle,
    }),
    [title, setTitle]
  )

  return (
    <PrivateNavigationContext.Provider value={value}>
      {children}
    </PrivateNavigationContext.Provider>
  )
}
