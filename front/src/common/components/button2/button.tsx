import {
  Button as ButtonDSFR,
  ButtonProps as ButtonDSFRProps,
} from "@codegouvfr/react-dsfr/Button"
import { ForwardedRef, forwardRef } from "react"

export type ButtonProps = ButtonDSFRProps

export const Button = forwardRef<
  HTMLButtonElement | HTMLAnchorElement,
  ButtonProps
>((props, ref) => {
  return props.linkProps ? (
    <ButtonDSFR {...props} ref={ref as ForwardedRef<HTMLAnchorElement>} />
  ) : (
    <ButtonDSFR {...props} ref={ref as ForwardedRef<HTMLButtonElement>} />
  )
})
