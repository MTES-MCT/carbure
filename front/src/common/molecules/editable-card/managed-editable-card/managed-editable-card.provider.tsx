import { ReactNode, createContext, useContext } from "react"
import { useSectionsManager } from "common/providers/sections-manager.provider"

interface ManagedEditableCardContextType {
  sectionId: string
  isExpanded: boolean
  setExpanded: (expanded: boolean) => void
  toggle: () => void
}

const ManagedEditableCardContext =
  createContext<ManagedEditableCardContextType | null>(null)

// Hook pour utiliser le contexte de section
export const useManagedEditableCard = () => {
  const context = useContext(ManagedEditableCardContext)
  if (!context) {
    throw new Error(
      "useManagedEditableCard must be used within ManagedEditableCardContextProvider"
    )
  }
  return context
}

interface ManagedEditableCardContextProviderProps {
  children: ReactNode
  sectionId: string
}

/**
 * Context provider that exposes the section ID and provides methods to open/close the section.
 * It integrates with the sections manager to handle the expanded state of editable cards.
 */
export const ManagedEditableCardContextProvider = ({
  children,
  sectionId,
}: ManagedEditableCardContextProviderProps) => {
  const { isSectionExpanded, setSectionExpanded, toggleSection } =
    useSectionsManager()

  const isExpanded = isSectionExpanded(sectionId)

  const setExpanded = (expanded: boolean) => {
    setSectionExpanded(sectionId, expanded)
  }

  const toggle = () => {
    toggleSection(sectionId)
  }

  const contextValue: ManagedEditableCardContextType = {
    sectionId,
    isExpanded,
    setExpanded,
    toggle,
  }

  return (
    <ManagedEditableCardContext.Provider value={contextValue}>
      {children}
    </ManagedEditableCardContext.Provider>
  )
}
