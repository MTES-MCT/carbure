import React, {
  createContext,
  useCallback,
  useContext,
  useLayoutEffect,
  useReducer,
  useRef,
} from "react"

/**
 * A registry allows collecting values from deeply nested children and listing them in the order they appear in the DOM
 */

interface RegistryValue<T> {
  entries: Entry<T>[]
  register: (value: T, label: React.ReactNode, node: HTMLElement) => void
  deregister: (value: T, label: React.ReactNode, node: HTMLElement) => void
  before: (value: T | undefined) => T | undefined
  after: (value: T | undefined) => T | undefined
}

export const RegistryContext = createContext<RegistryValue<any>>({
  entries: [],
  register: () => {},
  deregister: () => {},
  before: () => undefined,
  after: () => undefined,
})

interface Entry<T> {
  node: HTMLElement
  value: T
  label: React.ReactNode
}

interface Action<T> extends Entry<T> {
  type: "register" | "deregister"
}

function sortEntries<T>(a: Entry<T>, b: Entry<T>) {
  const position = a.node.compareDocumentPosition(b.node)
  return position & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
}

function registryReducer<T>(
  entries: Entry<T>[],
  action: Action<T>
): Entry<T>[] {
  const entry = { value: action.value, label: action.label, node: action.node }
  const hasValue = Boolean(entries.find((e) => e.value === entry.value))

  if (action.type === "register" && !hasValue) {
    return [...entries, entry].sort(sortEntries)
  }

  if (action.type === "deregister" && hasValue) {
    return entries.filter((e) => e.node !== entry.node).sort(sortEntries)
  }

  return entries
}

export function useRegistry<T>(): RegistryValue<T> {
  type RegistryReducer = React.Reducer<Entry<T>[], Action<T>>
  const [entries, dispatch] = useReducer<RegistryReducer>(registryReducer, [])

  const register = useCallback(
    (value: T, label: React.ReactNode, node: HTMLElement) => {
      dispatch({ type: "register", value, label, node })
    },
    []
  )

  const deregister = useCallback(
    (value: T, label: React.ReactNode, node: HTMLElement) => {
      dispatch({ type: "deregister", value, label, node })
    },
    []
  )

  const before = useCallback(
    (value: T | undefined) => {
      if (value === undefined) return entries[0]?.value ?? undefined
      const index = entries.findIndex((e) => e.value === value)
      const previous = Math.max(0, index - 1)
      return entries[previous].value
    },
    [entries]
  )

  const after = useCallback(
    (value: T | undefined) => {
      if (value === undefined) return entries[0]?.value ?? undefined
      const index = entries.findIndex((e) => e.value === value)
      const next = Math.min(index + 1, entries.length - 1)
      return entries[next].value
    },
    [entries]
  )

  return { entries, register, deregister, before, after }
}

type RegistryProps<T> = {
  value: RegistryValue<T>
  children: React.ReactNode
}

export function Registry<T>({ value, children }: RegistryProps<T>) {
  return (
    <RegistryContext.Provider value={value}>
      {children}
    </RegistryContext.Provider>
  )
}

export function useEntry<T, E extends HTMLElement>(
  value: T | undefined,
  label: React.ReactNode,
  domRef?: React.RefObject<E>
) {
  const registry = useContext<RegistryValue<T>>(RegistryContext)

  const localRef = useRef<E>(null)
  const ref = domRef ?? localRef

  useLayoutEffect(() => {
    if (typeof value === "undefined") return
    registry.register(value, label, ref.current!)
    return () => registry.deregister(value, label, ref.current!)
  }, [value, registry.register, registry.deregister])

  return { ref }
}

export default Registry
