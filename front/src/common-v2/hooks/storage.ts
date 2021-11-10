import { useCallback, useState } from "react"

function getKey<T>(key: string): T | undefined {
  const value = localStorage.getItem(key)
  return value && JSON.parse(value)
}

function setKey<T>(key: string, value: T) {
  const string = JSON.stringify(value)
  localStorage.setItem(key, string)
}

export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): [T, (value: T) => void, () => void] {
  const [state, setState] = useState(getKey<T>(key) ?? defaultValue)

  const setStateAndStorage = useCallback(
    (value: T) => {
      setState(value)
      setKey(key, value)
    },
    [key]
  )

  const emptyStateAndStorage = useCallback(() => {
    setState(defaultValue)
    localStorage.removeItem(key)
  }, [key, defaultValue])

  return [state, setStateAndStorage, emptyStateAndStorage]
}

export default useLocalStorage
