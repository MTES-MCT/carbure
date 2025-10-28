import { useSectionsManager } from "common/providers/sections-manager.provider"
import { EditableCard, EditableCardProps } from "../editable-card"
import { useEffect } from "react"
import {
  ManagedEditableCardContextProvider,
  useManagedEditableCard,
} from "./managed-editable-card.provider"
import { Form, FormProps } from "common/components/form2"

type ManagedEditableCardProps = EditableCardProps & {
  sectionId: string
}

/**
 * A wrapper around the EditableCard component that will manage the section expansion.
 */
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
    <ManagedEditableCardContextProvider sectionId={sectionId}>
      <EditableCard
        {...props}
        isEditing={isSectionExpanded(sectionId)}
        onEdit={(editing) => setSectionExpanded(sectionId, editing)}
      />
    </ManagedEditableCardContextProvider>
  )
}

const ManagedEditableCardForm = <T,>(props: FormProps<T>) => {
  const { setExpanded } = useManagedEditableCard()

  const onSubmit: FormProps<T>["onSubmit"] = async (...args) => {
    await props.onSubmit?.(...args)
    setExpanded(false)
  }
  return <Form {...props} onSubmit={onSubmit} />
}

ManagedEditableCard.Form = ManagedEditableCardForm
