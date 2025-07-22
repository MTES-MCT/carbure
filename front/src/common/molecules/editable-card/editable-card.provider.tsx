import { ReactNode, createContext, useContext, useState } from "react"

interface EditableCardContextType {
  isEditing: boolean
  setIsEditing: (editing: boolean) => void
}

const EditableCardContext = createContext<EditableCardContextType | null>(null)

// Hook pour utiliser le contexte
export const useEditableCard = () => {
  const context = useContext(EditableCardContext)
  if (!context) {
    throw new Error("useEditableCard must be used within EditableCard")
  }
  return context
}

interface EditableCardProviderProps {
  children: ReactNode
  defaultIsEditing?: boolean
  onEdit?: () => void
  onCancel?: () => void
}

export const EditableCardProvider = ({
  children,
  defaultIsEditing = false,
  onEdit,
  onCancel,
}: EditableCardProviderProps) => {
  const [isEditing, setIsEditing] = useState(defaultIsEditing)

  const handleSetIsEditing = (editing: boolean) => {
    setIsEditing(editing)
    if (editing) {
      onEdit?.()
    } else {
      onCancel?.()
    }
  }

  const contextValue: EditableCardContextType = {
    isEditing,
    setIsEditing: handleSetIsEditing,
  }

  return (
    <EditableCardContext.Provider value={contextValue}>
      {children}
    </EditableCardContext.Provider>
  )
}
