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

function parseValue<T>(el: FormTarget<T>) {
  if (el.type === "checkbox") {
    return el.checked
  } else if (el.type === "radio") {
    // if there are only two boolean-like options, convert to boolean
    return el.value === "true" || el.value === "false"
      ? el.value === "true"
      : el.value
  } else if (el.type === "number") {
    const parsed = parseFloat(`${el.value}`)
    return isNaN(parsed) ? "" : parsed
  } else {
    return el.value
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
      setState((data) => transform(options?.onChange, form, data))
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
