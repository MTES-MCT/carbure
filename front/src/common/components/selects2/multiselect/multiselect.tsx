import { lazy, Suspense } from "react"
import {
  MultiSelect as FilterMultiSelect,
  MultiSelectProps as FilterMultiSelectProps,
} from "../filter/multiselect"
import type { FormMultiSelectProps } from "../form/multiselect"

const LazyFormMultiSelect = lazy(() =>
  import("../form/multiselect").then((module) => ({
    default: module.FormMultiSelect,
  }))
) as <T, V = T>(props: FormMultiSelectProps<T, V>) => React.ReactElement | null

type FormVariantMultiSelectProps<T, V = T> = FormMultiSelectProps<T, V> & {
  variant: "form"
}

type FilterVariantMultiSelectProps<T, V = T> = FilterMultiSelectProps<T, V> & {
  variant?: "filter"
}

export type MultiSelectProps<T, V = T> =
  | FormVariantMultiSelectProps<T, V>
  | FilterVariantMultiSelectProps<T, V>

export function MultiSelect<T, V>(props: MultiSelectProps<T, V>) {
  if (props.variant === "form") {
    return (
      <Suspense fallback={null}>
        <LazyFormMultiSelect {...props} />
      </Suspense>
    )
  }

  return <FilterMultiSelect {...props} />
}
