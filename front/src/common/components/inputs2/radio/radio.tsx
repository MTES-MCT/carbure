import {
  RadioButtons,
  RadioButtonsProps,
} from "@codegouvfr/react-dsfr/RadioButtons"
import { ChangeEvent } from "react"

// Simplify the u
type OptionsProps = Omit<
  RadioButtonsProps["options"][number],
  "nativeInputProps"
> & {
  value: RadioButtonsProps["options"][number]["nativeInputProps"]["value"]
}

export type RadioGroupProps = Omit<RadioButtonsProps, "options"> & {
  options: OptionsProps[]
  value?: string | number
  onChange: (value: string) => void
}

export const RadioGroup = ({
  options,
  onChange,
  ...props
}: RadioGroupProps) => {
  const optionsWithNativeInputProps = options.map((option) => ({
    ...option,
    nativeInputProps: {
      value: option.value,
      onChange: (e: ChangeEvent<HTMLInputElement>) =>
        onChange?.(e.target.value),
      ...(Object.hasOwn(props, "value") // Handle uncontrolled value
        ? { checked: option.value === props.value }
        : {}),
    },
  }))

  return <RadioButtons {...props} options={optionsWithNativeInputProps} />
}
