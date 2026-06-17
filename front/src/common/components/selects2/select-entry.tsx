import { lazy, Suspense } from "react"
import {
  Select as ButtonSelect,
  SelectProps as ButtonSelectProps,
} from "./select"
import type { SelectDsfrProps } from "./select-dsfr"

const LazySelectDsfr = lazy(() =>
  import("./select-dsfr").then((module) => ({ default: module.SelectDsfr }))
) as <T, V = T>(props: SelectDsfrProps<T, V>) => React.ReactElement | null

type FieldSelectProps<T, V = T> = SelectDsfrProps<T, V> & {
  variant: "field"
}

type DefaultSelectProps<T, V = T> = ButtonSelectProps<T, V> & {
  variant?: undefined
}

export type SelectProps<T, V = T> =
  | FieldSelectProps<T, V>
  | DefaultSelectProps<T, V>

export function Select<T, V>(props: SelectProps<T, V>) {
  if (props.variant === "field") {
    return (
      <Suspense fallback={null}>
        <LazySelectDsfr {...props} />
      </Suspense>
    )
  }

  return <ButtonSelect {...props} />
}
