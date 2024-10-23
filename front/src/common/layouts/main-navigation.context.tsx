import {
  createContext,
  PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

interface MainNavigationContext {
  title: string
  setTitle: (title: string) => void
}
export const MainNavigationContext = createContext<MainNavigationContext>({
  title: "",
  setTitle: (title) => title,
})

export const useMainNavigation = (newTitle: string) => {
  const { setTitle } = useContext(MainNavigationContext)

  useEffect(() => {
    setTitle(newTitle)
  }, [newTitle, setTitle])
}

export const MainNavigationProvider = ({ children }: PropsWithChildren) => {
  const [title, setTitle] = useState("")

  const value = useMemo(
    () => ({
      title,
      setTitle,
    }),
    [title, setTitle]
  )

  return (
    <MainNavigationContext.Provider value={value}>
      {children}
    </MainNavigationContext.Provider>
  )
}
