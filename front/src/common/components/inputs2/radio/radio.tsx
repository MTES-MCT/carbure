import {
  RadioButtons,
  RadioButtonsProps,
} from "@codegouvfr/react-dsfr/RadioButtons"
import { ChangeEvent } from "react"
import { Label, LabelProps } from "../base-input"
import styles from "./radio.module.css"
import cl from "clsx"

type RadioValueType =
  RadioButtonsProps["options"][number]["nativeInputProps"]["value"]
// Simplify the usage of the RadioButtons component
type OptionsProps<V extends RadioValueType> = Omit<
  RadioButtonsProps["options"][number],
  "nativeInputProps"
> &
  Omit<LabelProps, "required"> & {
    value: V
  }

export type RadioGroupProps<V extends RadioValueType> = Omit<
  RadioButtonsProps,
  "options"
> & {
  options: OptionsProps<V>[]
  value?: V
  onChange?: (value: V) => void
} & LabelProps

export const RadioGroup = <V extends RadioValueType>({
  options,
  onChange,
  required,
  label,
  readOnly,
  hasTooltip,
  title,
  ...props
}: RadioGroupProps<V>) => {
  const optionsWithNativeInputProps = options.map((option) => ({
    ...option,
    nativeInputProps: {
      value: option.value,
      onChange: (e: ChangeEvent<HTMLInputElement>) =>
        onChange?.(e.target.value as V),
      ...(Object.hasOwn(props, "value") // Handle uncontrolled value
        ? { checked: option.value === props.value }
        : {}),
      required,
    },
  }))

  return (
    <RadioButtons
      {...props}
      options={optionsWithNativeInputProps}
      className={cl(
        props.className,
        styles["radio-group"],
        readOnly && styles["radio-group--read-only"]
      )}
      legend={
        <Label
          label={label}
          readOnly={readOnly}
          hasTooltip={hasTooltip}
          required={required}
          title={title}
        />
      }
      disabled={readOnly ?? props.disabled}
    />
  )
}
