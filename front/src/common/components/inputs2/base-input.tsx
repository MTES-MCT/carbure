import {
  Input as InputDSFR,
  InputProps as InputPropsDSFR,
} from "@codegouvfr/react-dsfr/Input"
import { Tooltip } from "@codegouvfr/react-dsfr/Tooltip"
import { ReactNode } from "react"
import { InformationLine } from "../icon"
import cl from "clsx"
import css from "./base-input.module.css"
import { Text } from "../text"

export type ExtendedInputProps = {
  loading?: boolean
  hasTooltip?: boolean
  // Content of the tooltip
  title?: ReactNode
  readOnly?: boolean
  autoFocus?: boolean
  name?: string
  pattern?: string
  placeholder?: string
  required?: boolean
  type?: string
  domRef?: React.RefObject<HTMLDivElement>
  label?: InputPropsDSFR["label"]
}
type BaseInputProps = InputPropsDSFR & ExtendedInputProps

/**
 * Base component for all inputs, including textarea and file inputs
 * It manages loading state, tooltip and custom label
 */
export const BaseInput = ({
  loading,
  hasTooltip,
  required,
  title,
  label,
  domRef,
  readOnly,
  ...props
}: BaseInputProps) => {
  // Set a custom style for read only inputs
  if (readOnly) {
    return (
      <div>
        <Label
          label={label}
          hasTooltip={hasTooltip}
          title={title}
          readOnly={readOnly}
        />
        <Text>
          {props.nativeInputProps?.value ?? props.nativeTextAreaProps?.value}
        </Text>
      </div>
    )
  }

  return (
    <InputDSFR
      {...props}
      iconId={loading ? "ri-loader-line" : props.iconId}
      label={
        <Label
          hasTooltip={hasTooltip}
          required={required}
          title={title}
          label={label}
        />
      }
      ref={domRef}
      className={cl(
        props.className,
        css["input-dsfr--no-margin"],
        props.state === "error" &&
          !props.stateRelatedMessage &&
          css["dsfr-input--error"]
      )}
    />
  )
}

export type LabelProps = Pick<
  BaseInputProps,
  "label" | "hasTooltip" | "required" | "title" | "readOnly"
>
export const Label = ({
  label,
  hasTooltip,
  required,
  title,
  readOnly,
}: LabelProps) => {
  let baseLabel = label

  // Add an icon if the input is required
  if (!readOnly && required) {
    baseLabel = `${baseLabel} *`
  }

  if (readOnly) {
    baseLabel = <span className={css["label--read-only"]}>{baseLabel}</span>
  }

  // Add a tooltip if the input has one
  if (hasTooltip) {
    baseLabel = (
      <Tooltip title={title}>
        {baseLabel}
        <InformationLine size="sm" style={{ marginLeft: "6px" }} />
      </Tooltip>
    )
  }

  return baseLabel
}
