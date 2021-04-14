import { useCallback, useRef, useState } from "react"

type FormOptions<T> = {
  onChange?: (nextState: T, prevState?: T) => T
}

export type FormState = Record<string, any>

export type FormTarget<T = any> = {
  type?: string
  value?: T[keyof T] | string | number | boolean
  name?: keyof T | string
  checked?: boolean
}

export type FormChangeHandler<T> = (e: { target: FormTarget<T> }) => void

function parseValue<T>(element: FormTarget<T>) {
  if (element.type === "checkbox") {
    return element.checked
  } else if (element.type === "number") {
    const parsed = parseFloat(`${element.value}`)
    return isNaN(parsed) ? "" : parsed
  } else {
    return element.value
  }
}

function transform<T extends FormState>(
  onChange: FormOptions<T>["onChange"] | undefined,
  nextState: T,
  prevState?: T
): T {
  if (!onChange) return nextState
  else return onChange(nextState, prevState)
}

export type FormHook<T extends FormState> = {
  data: T
  hasChange: boolean
  reset: (s: T) => void
  onChange: FormChangeHandler<T>
}

export default function useForm<T extends FormState>(
  initialState: T,
  options?: FormOptions<T>
): FormHook<T> {
  const hasChange = useRef(false)
  const [data, setState] = useState<T>(() =>
    transform(options?.onChange, { ...initialState })
  )

  const reset = useCallback(
    (form: T) => {
      hasChange.current = false
      setState(transform(options?.onChange, form))
    },
    [options?.onChange]
  )

  const onChange: FormChangeHandler<T> = (e) => {
    hasChange.current = true
    const nextState = { ...data, [`${e.target.name}`]: parseValue(e.target) }
    setState(transform(options?.onChange, nextState, data))
  }

  return {
    data,
    hasChange: hasChange.current,
    reset,
    onChange,
  }
}
