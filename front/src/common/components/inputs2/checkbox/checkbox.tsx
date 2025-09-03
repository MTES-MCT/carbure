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
import { Label, LabelProps } from "../base-input"

type CheckboxProps = Omit<CheckboxDSFRProps, "options" | "name"> & {
  value?: boolean
  captive?: boolean
  onChange?: (value: boolean) => void
  name?: string
} & LabelProps

export const Checkbox = ({
  label,
  value,
  onChange,
  captive = false,
  small,
  name,
  title,
  hasTooltip,
  readOnly,
  legend,
  className,
  ...props
}: CheckboxProps) => {
  const generatedId = useId()
  const id = props.id ?? generatedId
  const options: CheckboxDSFRProps["options"] = [
    {
      // label: label ? (
      //   <Label
      //     label={label}
      //     readOnly={readOnly}
      //     hasTooltip={hasTooltip}
      //     required={props.required}
      //     title={title}
      //   />
      // ) : (
      //   ""
      // ),
      label,
      nativeInputProps: {
        checked: value,
        onChange: (e: ChangeEvent<HTMLInputElement>) =>
          onChange?.(e.target.checked),
        onClick: captive ? (e) => e.stopPropagation() : undefined,
        disabled: props.disabled || readOnly,
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
          className,
          css["checkbox"],
          small && css["checkbox--small"]
        )}
        onClick={captive ? (e) => e.stopPropagation() : undefined}
        onChange={(e) => onChange?.(e.target.checked)}
        name={name}
      />
    )
  }
  return (
    <CheckboxDSFR
      {...props}
      options={options}
      small={small}
      className={cl(
        className,
        css["checkbox-group"],
        readOnly && css["checkbox--read-only"]
      )}
      legend={
        <Label
          label={legend}
          readOnly={readOnly}
          hasTooltip={hasTooltip}
          required={props.required}
          title={title}
        />
      }
    />
  )
}

export type CheckboxGroupProps<T, V> = Omit<
  CheckboxDSFRProps,
  "options" | "name" | "legend"
> & {
  options: T[]
  value: V[] | undefined
  onChange: (value: V[] | undefined) => void
  onToggle?: (value: V, checked: boolean) => void
  normalize?: Normalizer<T, V>
  name?: string
} & LabelProps

export const CheckboxGroup = <T, V extends string | number>({
  options,
  onChange,
  onToggle,
  normalize = defaultNormalizer,
  name,
  className,
  disabled,
  readOnly,
  hasTooltip,
  title,
  label,
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
      name,
      disabled: readOnly || disabled,
    },
  }))

  return (
    <div style={{ position: "relative" }}>
      {/* This is a hidden input that is used to validate the checkbox group */}
      <input
        type="text"
        required={props.required && (props.value?.length ?? 0) === 0}
        style={{
          width: 0,
          height: 0,
          opacity: 0,
          position: "absolute",
          top: "20px",
          left: 0,
          pointerEvents: "none",
        }}
        aria-hidden="true"
      />
      <CheckboxDSFR
        {...props}
        options={optionsWithNativeInputProps}
        className={cl(
          className,
          css["checkbox-group"],
          readOnly && css["checkbox--read-only"]
        )}
        legend={
          <Label
            label={label}
            readOnly={readOnly}
            hasTooltip={hasTooltip}
            required={props.required}
            title={title}
          />
        }
      />
    </div>
  )
}
