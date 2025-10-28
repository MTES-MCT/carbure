import { ReactNode, createContext, useContext, useState } from "react"

interface SectionState {
  [sectionId: string]: boolean
}

interface SectionsManagerContextType {
  sections: SectionState
  toggleSection: (sectionId: string) => void
  setSectionExpanded: (sectionId: string, expanded: boolean) => void
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
      [sectionId]: !prev[sectionId],
    }))
  }

  const setSectionExpanded = (sectionId: string, expanded: boolean) => {
    setSections((prev) => ({
      ...prev,
      [sectionId]: expanded,
    }))
  }

  const expandAll = () => {
    setSections((prev) => {
      const newSections = { ...prev }
      Object.keys(newSections).forEach((key) => {
        newSections[key] = true
      })
      return newSections
    })
  }

  const collapseAll = () => {
    setSections((prev) => {
      const newSections = { ...prev }
      Object.keys(newSections).forEach((key) => {
        newSections[key] = false
      })
      return newSections
    })
  }

  const registerSection = (sectionId: string, expanded: boolean = false) => {
    // Register a section only if it is not already registered
    setSections((prev) => {
      if (prev[sectionId]) return prev

      return {
        ...prev,
        [sectionId]: expanded,
      }
    })
  }

  const isSectionExpanded = (sectionId: string) => {
    return sections[sectionId] || false
  }

  const contextValue: SectionsManagerContextType = {
    sections,
    toggleSection,
    setSectionExpanded,
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
