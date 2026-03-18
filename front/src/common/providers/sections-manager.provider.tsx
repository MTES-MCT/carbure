import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useState,
} from "react"

interface SectionState {
  [sectionId: string]: {
    expanded: boolean
    isError: boolean
  }
}

interface SectionsManagerContextType {
  sections: SectionState
  toggleSection: (sectionId: string) => void
  setSectionExpanded: (sectionId: string, expanded: boolean) => void
  setSectionError: (sectionId: string, isError: boolean) => void
  expandAll: () => void
  collapseAll: () => void
  isSectionExpanded: (sectionId: string) => boolean
  registerSection: (sectionId: string, expanded: boolean) => void
}

const SectionsManagerContext = createContext<SectionsManagerContextType | null>(
  null
)

export const useSectionsManager = () => {
  const context = useContext(SectionsManagerContext)
  if (!context) {
    throw new Error(
      "useSectionsManager must be used within SectionsManagerProvider"
    )
  }
  return context
}

interface SectionsManagerProviderProps {
  children: ReactNode
  defaultSections?: SectionState
}

export const SectionsManagerProvider = ({
  children,
  defaultSections = {},
}: SectionsManagerProviderProps) => {
  const [sections, setSections] = useState<SectionState>(defaultSections)

  const toggleSection = (sectionId: string) => {
    setSections((prev) => ({
      ...prev,
      [sectionId]: {
        expanded: !prev[sectionId]?.expanded,
        isError: false,
      },
    }))
  }

  const setSectionExpanded = (sectionId: string, expanded: boolean) => {
    setSections((prev) => ({
      ...prev,
      [sectionId]: {
        expanded,
        isError: false,
      },
    }))
  }

  const expandAll = () => {
    setSections((prev) => {
      const newSections = { ...prev }
      Object.keys(newSections).forEach((key) => {
        if (prev[key]?.expanded) {
          newSections[key] = {
            expanded: true,
            isError: false,
          }
        }
      })
      return newSections
    })
  }

  const collapseAll = () => {
    setSections((prev) => {
      const newSections = { ...prev }
      Object.keys(newSections).forEach((key) => {
        if (prev[key]?.expanded) {
          newSections[key] = {
            expanded: false,
            isError: false,
          }
        }
      })
      return newSections
    })
  }

  const registerSection = (sectionId: string, expanded: boolean = false) => {
    // Register a section only if it is not already registered
    setSections((prev) => {
      if (sectionId in prev) return prev

      return {
        ...prev,
        [sectionId]: {
          expanded,
          isError: false,
        },
      }
    })
  }

  const setSectionError = useCallback((sectionId: string, isError: boolean) => {
    setSections((prev) => {
      if (!prev[sectionId]) return prev
      return {
        ...prev,
        [sectionId]: {
          ...prev[sectionId],
          isError,
        },
      }
    })
  }, [])

  const isSectionExpanded = (sectionId: string) => {
    return sections[sectionId]?.expanded || false
  }

  const contextValue: SectionsManagerContextType = {
    sections,
    toggleSection,
    setSectionExpanded,
    setSectionError,
    expandAll,
    collapseAll,
    isSectionExpanded,
    registerSection,
  }

  return (
    <SectionsManagerContext.Provider value={contextValue}>
      {children}
    </SectionsManagerContext.Provider>
  )
}
