import {
  ToggleSwitch as ToggleSwitchDSFR,
  ToggleSwitchProps as ToggleSwitchDSFRProps,
} from "@codegouvfr/react-dsfr/ToggleSwitch"
import { forwardRef } from "react"

export type ToggleSwitchProps =
  | (Omit<ToggleSwitchDSFRProps.Controlled, "checked" | "inputTitle"> & {
      value: boolean
    })
  | (Omit<ToggleSwitchDSFRProps.Uncontrolled, "checked" | "inputTitle"> & {
      value?: never
    })

export const ToggleSwitch = forwardRef<HTMLDivElement, ToggleSwitchProps>(
  ({ value, ...props }, ref) => {
    const toggleSwitchProps =
      value === undefined ? props : { ...props, checked: value }

    return (
      <ToggleSwitchDSFR
        {...(toggleSwitchProps as ToggleSwitchDSFRProps)}
        ref={ref}
      />
    )
  }
)
