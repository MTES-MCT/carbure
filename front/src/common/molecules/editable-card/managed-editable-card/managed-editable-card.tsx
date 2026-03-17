import { useSectionsManager } from "common/providers/sections-manager.provider"
import { EditableCard, EditableCardProps } from "../editable-card"
import { useEffect } from "react"
import {
  ManagedEditableCardContextProvider,
  useManagedEditableCard,
} from "./managed-editable-card.provider"
import { Form, FormProps } from "common/components/form2"
import clsx from "clsx"
import css from "./managed-editable-card.module.css"

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
  const { sections, isSectionExpanded, setSectionExpanded, registerSection } =
    useSectionsManager()

  // Register the section in the sections manager
  useEffect(() => {
    registerSection(sectionId, isSectionExpanded(sectionId))
  }, [])

  const sectionState = sections[sectionId]
  const isError = sectionState?.isError ?? false

  return (
    <ManagedEditableCardContextProvider sectionId={sectionId}>
      <EditableCard
        {...props}
        isEditing={isSectionExpanded(sectionId)}
        onEdit={(editing) => setSectionExpanded(sectionId, editing)}
        id={sectionId}
        className={clsx(isError && css["managed-editable-card--error"])}
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
