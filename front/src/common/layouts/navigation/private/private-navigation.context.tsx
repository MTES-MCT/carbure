import {
  createContext,
  PropsWithChildren,
  ReactElement,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react"

interface PrivateNavigationContext {
  title?: ReactElement | string | undefined
  setTitle: (title: ReactElement | string) => void
}
export const PrivateNavigationContext = createContext<PrivateNavigationContext>(
  {
    title: "",
    setTitle: (title) => title,
  }
)

export const usePrivateNavigation = (
  newTitle?: ReactElement | string,
  key?: string
) => {
  const { setTitle } = useContext(PrivateNavigationContext)
  const _key = typeof newTitle !== "string" ? key : newTitle

  if (newTitle && typeof newTitle !== "string" && !key) {
    throw new Error("Key is required when newTitle is not a string")
  }

  // Title need to be updated only when the key changes (to prevent infinite re-renders with a react element)
  useEffect(() => {
    setTitle(newTitle ?? "")
  }, [_key])

  return { setTitle }
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
