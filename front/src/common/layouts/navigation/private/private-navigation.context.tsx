import {
  createContext,
  PropsWithChildren,
  ReactElement,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"

interface PrivateNavigationContext {
  title?: ReactElement | string
  setTitle: (title: ReactElement | string) => void
}
export const PrivateNavigationContext = createContext<PrivateNavigationContext>(
  {
    title: "",
    setTitle: (title) => title,
  }
)

export const usePrivateNavigation = (newTitle: ReactElement | string) => {
  const { setTitle } = useContext(PrivateNavigationContext)
  const ref = useRef(newTitle)

  // Title need to be updated only when the ref changes (to prevent infinite re-renders with a react element)
  useEffect(() => {
    setTitle(ref.current)
  }, [ref])
}

export const PrivateNavigationProvider = ({ children }: PropsWithChildren) => {
  const [title, setTitle] = useState<ReactElement | string | undefined>("")

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
