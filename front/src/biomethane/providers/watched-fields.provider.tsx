import { createContext, ReactNode, useContext } from "react"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"

export interface WatchedFieldsContextValue<T extends object> {
  /** Liste des champs surveillés */
  watchedFields: string[]
  /** Fonction pour vérifier si un champ est surveillé */
  hasWatchedFieldsChanged: (obj: Partial<T>, form: Partial<T>) => boolean
}

const createWatchedFieldsContext = <T extends object>() => {
  return createContext<WatchedFieldsContextValue<T> | null>(null)
}

interface WatchedFieldsProviderProps {
  children: ReactNode
  /** Fonction API qui retourne un tableau de champs */
  apiFunction: (entity_id: number) => Promise<string[]>
  /** Clé unique pour le cache de la requête */
  queryKey: string
}

/**
 * Provider pour gérer les champs surveillés.
 *
 * Ce provider centralise la logique de récupération et de vérification des champs surveillés :
 * - Récupère la liste des champs via une fonction API
 * - Fournit une fonction has() pour vérifier si un champ est surveillé
 * - Met en cache les résultats pour éviter les requêtes répétées
 *
 * Les composants enfants peuvent accéder à ces données via le hook useWatchedFields().
 */
export function WatchedFieldsProvider<T extends object>({
  children,
  apiFunction,
  queryKey,
}: WatchedFieldsProviderProps) {
  const entity = useEntity()
  const { result: watchedFields = [] } = useQuery(apiFunction, {
    key: queryKey,
    params: [entity.id],
  })

  const WatchedFieldsContext = createWatchedFieldsContext<T>()

  const hasWatchedFieldsChanged = (contract: Partial<T>, form: Partial<T>) => {
    const fields = Object.entries(form).filter(
      ([key, value]) => contract[key as keyof T] !== value
    )
    return fields.some(([key]) => watchedFields.includes(key))
  }

  const value: WatchedFieldsContextValue<T> = {
    watchedFields,
    hasWatchedFieldsChanged,
  }

  return (
    <WatchedFieldsContext.Provider value={value}>
      {children}
    </WatchedFieldsContext.Provider>
  )
}

export function useWatchedFields<
  T extends object,
>(): WatchedFieldsContextValue<T> {
  const WatchedFieldsContext = createWatchedFieldsContext<T>()

  const ctx = useContext(WatchedFieldsContext)
  if (!ctx) {
    throw new Error(
      "useWatchedFields doit être utilisé dans un WatchedFieldsProvider"
    )
  }
  return ctx
}
