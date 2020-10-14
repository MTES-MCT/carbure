import { useState } from "react"

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
  <T extends FormFields>(e: React.ChangeEvent<T>) => void,
  React.Dispatch<React.SetStateAction<T>>
]

export default function useForm<T>(initialState: T): FormHook<T> {
  const [form, setForm] = useState<T>(initialState)

  function change<T extends FormFields>(e: React.ChangeEvent<T>) {
    setForm({
      ...form,
      [e.target.name]: parseValue(e.target),
    })
  }

  return [form, change, setForm]
}
