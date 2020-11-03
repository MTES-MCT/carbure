import { useRef, useState } from "react"

export type FormFields = HTMLInputElement | HTMLTextAreaElement

function isCheckbox(element: FormFields): element is HTMLInputElement {
  return element.tagName === "INPUT" && element.type === "checkbox"
}

function parseValue(element: FormFields) {
  if (isCheckbox(element)) {
    return element.checked
  } else if (element.type === "number") {
    return parseFloat(element.value)
  } else {
    return element.value
  }
}

export type FormHook<T> = [
  T,
  boolean,
  <T extends FormFields>(e: React.ChangeEvent<T>) => void,
  (s: T) => void
]

export default function useForm<T>(initialState: T): FormHook<T> {
  const [form, setFormState] = useState<T>(initialState)
  const hasChange = useRef(false)

  function change<U extends FormFields>(e: React.ChangeEvent<U>) {
    hasChange.current = true

    setFormState({
      ...form,
      [e.target.name]: parseValue(e.target),
    })
  }

  function setForm(state: T) {
    hasChange.current = false
    setFormState(state)
  }

  return [form, hasChange.current, change, setForm]
}
