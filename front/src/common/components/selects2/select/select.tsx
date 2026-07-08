import { lazy, Suspense } from "react"
import { FilterSelect, FilterSelectProps } from "../filter/select"
import type { FormSelectProps } from "../form/select"

const LazyFormSelect = lazy(() =>
  import("../form/select").then((module) => ({ default: module.FormSelect }))
) as <T, V = T>(props: FormSelectProps<T, V>) => React.ReactElement | null

type FormVariantSelectProps<T, V = T> = FormSelectProps<T, V> & {
  variant: "form"
}

type FilterVariantSelectProps<T, V = T> = FilterSelectProps<T, V> & {
  variant?: "filter"
}

export type SelectProps<T, V = T> =
  | FormVariantSelectProps<T, V>
  | FilterVariantSelectProps<T, V>

export function Select<T, V>(props: SelectProps<T, V>) {
  if (props.variant === "form") {
    return (
      <Suspense fallback={null}>
        <LazyFormSelect {...props} />
      </Suspense>
    )
  }

  return <FilterSelect {...props} />
}
