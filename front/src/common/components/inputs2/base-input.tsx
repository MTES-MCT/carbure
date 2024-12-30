import { Input, InputProps } from "@codegouvfr/react-dsfr/Input"
import { Tooltip } from "@codegouvfr/react-dsfr/Tooltip"
import { forwardRef, ReactNode } from "react"
import { InformationLine } from "../icon"

export type BaseInputProps = InputProps & {
  loading?: boolean
  hasTooltip?: boolean
  // Content of the tooltip
  title?: ReactNode
}

export const BaseInput = forwardRef<HTMLDivElement, BaseInputProps>(
  ({ loading, ...props }, ref) => {
    const renderLabel = () => {
      let baseLabel = props.label

      // Add an icon if the input is required
      if (
        props.nativeInputProps?.required ||
        props.nativeTextAreaProps?.required
      ) {
        baseLabel = `${baseLabel} *`
      }

      // Add a tooltip if the input has one
      if (props.hasTooltip) {
        baseLabel = (
          <Tooltip title={props.title}>
            {baseLabel}
            <InformationLine size="sm" style={{ marginLeft: "6px" }} />
          </Tooltip>
        )
      }
      return baseLabel
    }
    return (
      <Input
        {...props}
        ref={ref}
        iconId={loading ? "ri-loader-line" : props.iconId}
        label={renderLabel()}
      />
    )
  }
)
