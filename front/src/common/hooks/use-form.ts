import { useCallback, useRef, useState } from "react"

export type FormFields = HTMLInputElement | HTMLTextAreaElement

function isCheckbox(element: FormFields): element is HTMLInputElement {
  return element.tagName === "INPUT" && element.type === "checkbox"
}

function parseValue(element: FormFields) {
  if (isCheckbox(element)) {
    return element.checked
  } else if (element.type === "number") {
    const parsed = parseFloat(element.value)
    return isNaN(parsed) ? 0 : parsed
  } else {
    return element.value
  }
}

export type FormHook<T> = {
  data: T
  hasChange: boolean
  reset: (s: T) => void
  patch: (p: any, s?: boolean) => void
  onChange: <T extends FormFields>(e: React.ChangeEvent<T>) => void
}

export default function useForm<T>(initialState: T): FormHook<T> {
  const [data, setData] = useState<T>(initialState)
  const hasChange = useRef(false)

  const patch = useCallback(
    (patch: any, silent: boolean = false) => {
      if (!silent) hasChange.current = true
      setData({ ...data, ...patch })
    },
    [data]
  )

  const reset = useCallback((form: T) => {
    hasChange.current = false
    setData(form)
  }, [])

  function onChange<U extends FormFields>(e: React.ChangeEvent<U>) {
    patch({ [e.target.name]: parseValue(e.target) })
  }

  return {
    data,
    hasChange: hasChange.current,
    patch,
    reset,
    onChange,
  }
}
