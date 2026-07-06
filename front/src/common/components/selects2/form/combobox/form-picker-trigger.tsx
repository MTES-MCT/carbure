import { BaseInput, LabelProps } from "common/components/inputs2/base-input"
import { InputProps } from "common/components/inputs2/input"
import cl from "clsx"
import { RefObject } from "react"
import styles from "./form-picker.module.css"

export type FormPickerTriggerProps = Omit<
  InputProps,
  "value" | "onChange" | "nativeInputProps" | "inputRef" | "iconId" | "readOnly"
> &
  Pick<LabelProps, "hasTooltip" | "title"> & {
    triggerRef: RefObject<HTMLInputElement>
    displayValue: string
  }

export function FormPickerTrigger({
  label,
  required,
  triggerRef,
  displayValue,
  name,
  placeholder,
  className,
  ...props
}: FormPickerTriggerProps) {
  return (
    <BaseInput
      {...props}
      required={required}
      className={cl(className, styles["form-picker-trigger"])}
      iconId="fr-icon-arrow-down-s-line"
      label={label}
      nativeInputProps={{
        ref: triggerRef,
        name,
        value: displayValue,
        readOnly: true,
        placeholder,
      }}
    />
  )
}
