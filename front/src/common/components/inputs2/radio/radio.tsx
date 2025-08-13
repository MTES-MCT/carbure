import {
  RadioButtons,
  RadioButtonsProps,
} from "@codegouvfr/react-dsfr/RadioButtons"
import { ChangeEvent } from "react"
import { Label, LabelProps } from "../base-input"
import styles from "./radio.module.css"
import cl from "clsx"
import { Text } from "common/components/text"

// The DSFR does not support boolean values for the radio buttons
type RadioValueType =
  | RadioButtonsProps["options"][number]["nativeInputProps"]["value"]
  | boolean
  | null

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
} & Omit<LabelProps, "label"> & {
    label?: LabelProps["label"]
  }

// The value returned by the onChange event from the DSFR is a string, so we need to convert it to the correct type
const convertValue = <V extends RadioValueType>(
  onChangeValue: string,
  value: V
) => {
  if (typeof value === "boolean") return onChangeValue === "true"
  if (typeof value === "number") return Number(onChangeValue)
  if (typeof value === "string") return onChangeValue

  return onChangeValue as V
}

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
  if (readOnly) {
    // Get the label value from the options if a value is provided
    const labelValue =
      props.value !== undefined && props.value !== null
        ? options.find((option) => option.value === props.value)?.label
        : "-"
    return (
      <div>
        <Label
          label={label}
          hasTooltip={hasTooltip}
          title={title}
          readOnly={readOnly}
        />
        <Text size="sm">{labelValue}</Text>
      </div>
    )
  }

  const optionsWithNativeInputProps = options.map((option) => ({
    ...option,
    nativeInputProps: {
      value: option.value,
      onChange: (e: ChangeEvent<HTMLInputElement>) => {
        const value = convertValue(e.target.value, option.value) as V
        return onChange?.(value)
      },
      ...(Object.hasOwn(props, "value") // Handle uncontrolled value
        ? { checked: option.value === props.value }
        : {}),
      required,
    },
  })) as RadioButtonsProps["options"]

  return (
    <RadioButtons
      {...props}
      options={optionsWithNativeInputProps}
      className={cl(
        props.className,
        styles["radio-group"],
        props.orientation === "horizontal" && styles["radio-group--horizontal"],
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
      small={readOnly ?? props.small}
    />
  )
}
