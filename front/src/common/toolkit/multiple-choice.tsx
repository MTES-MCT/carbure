import React, { useContext } from "react"
import { noop } from "./types"

interface MultipleChoiceValue<T> {
  value: T[]
  name: string
  onChange: (value: T) => void
}

const MultipleChoiceContext = React.createContext<MultipleChoiceValue<any>>({
  value: [],
  name: "",
  onChange: () => {},
})

export type MultipleChoiceProps<T> = {
  value?: T[]
  name?: string
  onChange?: (value: T[]) => void
  children: React.ReactNode
}

export function MultipleChoice<T>({
  value = [],
  name = "",
  children,
  onChange: setValue = noop,
}: MultipleChoiceProps<T>) {
  function onChange(item: T) {
    if (value.includes(item)) {
      setValue(value.filter((c) => c !== item))
    } else {
      setValue([...value, item])
    }
  }

  return (
    <MultipleChoiceContext.Provider value={{ value, name, onChange }}>
      {children}
    </MultipleChoiceContext.Provider>
  )
}

export function useMultipleChoice<T>() {
  return useContext<MultipleChoiceValue<T>>(MultipleChoiceContext)
}

export default MultipleChoice
