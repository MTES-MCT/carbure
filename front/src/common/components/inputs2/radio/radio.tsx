import {
  RadioButtons,
  RadioButtonsProps,
} from "@codegouvfr/react-dsfr/RadioButtons"
import { ChangeEvent } from "react"
import styles from "./radio.module.css"
import cl from "clsx"

// Simplify the u
type OptionsProps<
  V extends RadioButtonsProps["options"][number]["nativeInputProps"]["value"],
> = Omit<RadioButtonsProps["options"][number], "nativeInputProps"> & {
  value: V
}

export type RadioGroupProps<
  V extends RadioButtonsProps["options"][number]["nativeInputProps"]["value"],
> = Omit<RadioButtonsProps, "options"> & {
  options: OptionsProps<V>[]
  value?: V
  onChange: (value: V) => void
}

export const RadioGroup = <
  V extends RadioButtonsProps["options"][number]["nativeInputProps"]["value"],
>({
  options,
  onChange,
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
    },
  }))

  return (
    <RadioButtons
      {...props}
      options={optionsWithNativeInputProps}
      className={cl(props.className, styles["radio-group"])}
    />
  )
}
