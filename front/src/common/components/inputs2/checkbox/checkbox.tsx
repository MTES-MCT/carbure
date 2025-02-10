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
import { ChangeEvent } from "react"
import cl from "clsx"
import { fr } from "@codegouvfr/react-dsfr"
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
      <div
        className={cl(
          css["checkbox-without-label"],
          fr.cx("fr-checkbox-group"),
          small && fr.cx("fr-checkbox-group--sm"),
          small && css["checkbox-without-label--small"]
        )}
      >
        <input
          type="checkbox"
          {...props}
          checked={value ?? false}
          onChange={onChange ? (e) => onChange(e.target.checked) : undefined}
        />
        <label
          className={cl(
            fr.cx("fr-label"),
            css["checkbox-without-label__no-margin"]
          )}
          htmlFor={props.id}
        />
      </div>
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
