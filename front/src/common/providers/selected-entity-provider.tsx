import { createContext, useContext, useState } from "react"

/**
 * This provider is used to propagate the selected entity in the tree of components
 * It is used in the admin view to show informations related to the selected entity
 * (ex: show biomethane admin view)
 */
interface SelectedEntityContextType {
  selectedEntityId: number | undefined
  setSelectedEntityId: (entityId: number | undefined) => void
  hasSelectedEntity: boolean
}

const SelectedEntityContext = createContext<
  SelectedEntityContextType | undefined
>(undefined)

export const SelectedEntityProvider = ({
  children,
}: {
  children: React.ReactNode
}) => {
  const [selectedEntityId, setSelectedEntityId] = useState<number | undefined>(
    undefined
  )

  return (
    <SelectedEntityContext.Provider
      value={{
        selectedEntityId,
        setSelectedEntityId,
        hasSelectedEntity: selectedEntityId !== undefined,
      }}
    >
      {children}
    </SelectedEntityContext.Provider>
  )
}

export const useSelectedEntity = () => {
  const context = useContext(SelectedEntityContext)
  if (!context) {
    // If the context is not found, return a default value to avoid pass provider when the hooks is used
    return {
      selectedEntityId: undefined,
      setSelectedEntityId: () => {},
      hasSelectedEntity: false,
    }
  }
  return context
}
