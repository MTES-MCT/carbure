import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useMemo,
} from "react"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export interface WatchedFieldsContextValue<T extends object> {
  /** List of watched fields */
  watchedFields: string[]
  /** Function to check if a field is watched */
  hasWatchedFieldsChanged: (obj: Partial<T>, form: Partial<T>) => boolean
}

const WatchedFieldsContext =
  createContext<WatchedFieldsContextValue<object> | null>(null)

interface WatchedFieldsProviderProps {
  children: ReactNode
  /** API function that returns an array of fields */
  apiFunction: (
    entity_id: number,
    selectedEntityId?: number
  ) => Promise<string[]>
  /** Unique key for query cache */
  queryKey: string
}

/**
 * Provider for managing watched fields.
 *
 * This provider centralizes the logic for retrieving and checking watched fields:
 * - Retrieves the list of fields via an API function
 * - Provides a hasWatchedFieldsChanged() function to check if the watched fields have changed
 *
 * Child components can access this data via the useWatchedFields() hook.
 */
export function WatchedFieldsProvider<T extends object>({
  children,
  apiFunction,
  queryKey,
}: WatchedFieldsProviderProps) {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const { result: watchedFields = [] } = useQuery(apiFunction, {
    key: queryKey,
    params: [entity.id, selectedEntityId],
  })

  const hasWatchedFieldsChanged = useCallback(
    (contract: Partial<T>, form: Partial<T>) => {
      const fields = Object.entries(form).filter(
        ([key, value]) => contract[key as keyof T] !== value
      )
      return fields.some(([key]) => watchedFields.includes(key))
    },
    [watchedFields]
  )

  const value: WatchedFieldsContextValue<T> = useMemo(
    () => ({
      watchedFields,
      hasWatchedFieldsChanged,
    }),
    [watchedFields, hasWatchedFieldsChanged]
  )

  return (
    <WatchedFieldsContext.Provider value={value}>
      {children}
    </WatchedFieldsContext.Provider>
  )
}

export function useWatchedFields<
  T extends object,
>(): WatchedFieldsContextValue<T> {
  const ctx = useContext<WatchedFieldsContextValue<T> | null>(
    WatchedFieldsContext
  )
  if (!ctx) {
    throw new Error(
      "useWatchedFields must be used within a WatchedFieldsProvider"
    )
  }
  return ctx
}
