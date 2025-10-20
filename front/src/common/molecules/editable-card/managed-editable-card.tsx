import { useSectionsManager } from "common/providers/sections-manager.provider"
import { EditableCard, EditableCardProps } from "./editable-card"
import { useEffect } from "react"

type ManagedEditableCardProps = EditableCardProps & {
  sectionId: string
}
export const ManagedEditableCard = ({
  sectionId,
  ...props
}: ManagedEditableCardProps) => {
  const { isSectionExpanded, setSectionExpanded, registerSection } =
    useSectionsManager()

  // Register the section in the sections manager
  useEffect(() => {
    registerSection(sectionId, isSectionExpanded(sectionId))
  }, [])

  return (
    <EditableCard
      {...props}
      isEditing={isSectionExpanded(sectionId)}
      onEdit={(editing) => setSectionExpanded(sectionId, editing)}
    />
  )
}
