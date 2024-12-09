import {
  Button as ButtonDSFR,
  ButtonProps as ButtonDSFRProps,
} from "@codegouvfr/react-dsfr/Button"
import { ForwardedRef, forwardRef } from "react"
import cl from "clsx"
import css from "./button.module.css"

export type ButtonProps = ButtonDSFRProps & {
  // For our cases, we want to use the link style with a button
  customPriority?: "link"
}

export const Button = forwardRef<
  HTMLButtonElement | HTMLAnchorElement,
  ButtonProps
>((props, ref) => {
  if (props.customPriority === "link") {
    return (
      <button
        {...props}
        ref={ref as ForwardedRef<HTMLButtonElement>}
        className={cl(props.className, css["button-as-link-style"])}
      >
        {props.children}
      </button>
    )
  }

  return props.linkProps ? (
    <ButtonDSFR {...props} ref={ref as ForwardedRef<HTMLAnchorElement>} />
  ) : (
    <ButtonDSFR {...props} ref={ref as ForwardedRef<HTMLButtonElement>} />
  )
})
