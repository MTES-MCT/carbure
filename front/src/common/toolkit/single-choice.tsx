import React, { useContext } from "react"
import { noop } from "./types"

interface SingleChoiceValue<T> {
  value: T
  name: string
  onChange: (value: T) => void
}

const SingleChoiceContext = React.createContext<SingleChoiceValue<any>>({
  value: undefined,
  name: "",
  onChange: () => {},
})

export type SingleChoiceProps<T> = {
  value?: T
  name?: string
  onChange?: (value: T) => void
  children: React.ReactNode
}

export function SingleChoice<T>({
  value,
  name = "",
  children,
  onChange = noop,
}: SingleChoiceProps<T>) {
  return (
    <SingleChoiceContext.Provider value={{ value, name, onChange }}>
      {children}
    </SingleChoiceContext.Provider>
  )
}

export function useSingleChoice<T>() {
  return useContext<SingleChoiceValue<T>>(SingleChoiceContext)
}

export default SingleChoice
