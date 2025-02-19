import {
  Checkbox as CheckboxDSFR,
  CheckboxProps as CheckboxDSFRProps,
} from "@codegouvfr/react-dsfr/Checkbox"
import {
  defaultNormalizer,
  normalizeItems,
  Normalizer,
} from "common/utils/normalize"
import { multipleSelection } from "common/utils/selection"
import { ChangeEvent, useId } from "react"
import cl from "clsx"
import css from "./checkbox.module.css"

type CheckboxProps = Omit<CheckboxDSFRProps, "options"> & {
  label?: string
  value?: boolean
  captive?: boolean
  onChange?: (value: boolean) => void
}

export const Checkbox = ({
  label,
  value,
  onChange,
  captive = false,
  small,
  ...props
}: CheckboxProps) => {
  const generatedId = useId()
  const id = props.id ?? generatedId
  const options: CheckboxDSFRProps["options"] = [
    {
      label: label ?? "",
      nativeInputProps: {
        checked: value,
        onChange: (e: ChangeEvent<HTMLInputElement>) =>
          onChange?.(e.target.checked),
        onClick: captive ? (e) => e.stopPropagation() : undefined,
      },
    },
  ]

  // The checkbox DSFR component does not support checkbox without label
  if (!label) {
    return (
      <input
        {...props}
        type="checkbox"
        checked={value ?? false}
        id={id}
        className={cl(
          props.className,
          css["checkbox"],
          small && css["checkbox--small"]
        )}
        onClick={captive ? (e) => e.stopPropagation() : undefined}
        onChange={(e) => onChange?.(e.target.checked)}
      />
    )
  }
  return <CheckboxDSFR {...props} options={options} small={small} />
}

export type CheckboxGroupProps<T, V> = Omit<CheckboxDSFRProps, "options"> & {
  options: T[]
  value: V[] | undefined
  onChange: (value: V[] | undefined) => void
  onToggle?: (value: V, checked: boolean) => void
  normalize?: Normalizer<T, V>
}
export const CheckboxGroup = <T, V extends string | number>({
  options,
  onChange,
  onToggle,
  normalize = defaultNormalizer,
  ...props
}: CheckboxGroupProps<T, V>) => {
  const selection = multipleSelection(props.value, onChange)
  const normOptions = normalizeItems(options, normalize)
  const optionsWithNativeInputProps = normOptions.map((option) => ({
    ...option,
    nativeInputProps: {
      onChange: (e: ChangeEvent<HTMLInputElement>) => {
        selection.onSelect(option.value)
        onToggle?.(option.value, e.target.checked)
      },
      ...(Object.hasOwn(props, "value") // Handle uncontrolled value
        ? { checked: selection.isSelected(option.value) }
        : {}),
    },
  }))
  return <CheckboxDSFR {...props} options={optionsWithNativeInputProps} />
}
