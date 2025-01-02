import {
  Input as InputDSFR,
  InputProps as InputPropsDSFR,
} from "@codegouvfr/react-dsfr/Input"
import { Tooltip } from "@codegouvfr/react-dsfr/Tooltip"
import { forwardRef, ReactNode } from "react"
import { InformationLine } from "../icon"

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
}
type BaseInputProps = InputPropsDSFR & ExtendedInputProps

/**
 * Base component for all inputs, including textarea
 * It manages loading state, tooltip and custom label
 */
export const BaseInput = forwardRef<HTMLDivElement, BaseInputProps>(
  ({ loading, hasTooltip, required, title, label, ...props }, ref) => {
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
        ref={ref}
      />
    )
  }
)

type LabelProps = Pick<
  BaseInputProps,
  "label" | "hasTooltip" | "required" | "title"
>
const Label = ({ label, hasTooltip, required, title }: LabelProps) => {
  let baseLabel = label

  // Add an icon if the input is required
  if (required) {
    baseLabel = `${baseLabel} *`
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
