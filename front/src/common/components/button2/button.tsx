import {
  Button as ButtonDSFR,
  ButtonProps as ButtonDSFRProps,
} from "@codegouvfr/react-dsfr/Button"
import { forwardRef } from "react"
import cl from "clsx"
import css from "./button.module.css"
import { layout, Layout } from "../scaffold"

export type ButtonProps = ButtonDSFRProps &
  Layout & {
    // For our cases, we want to use the link style with a button
    customPriority?: "link" | "danger" | "success"
    loading?: boolean
  }

export const BaseButton = forwardRef<HTMLButtonElement, ButtonProps>(
  (props, ref) =>
    !props.linkProps ? (
      <ButtonDSFR
        {...props}
        ref={ref}
        {...layout(props)}
        disabled={Boolean(props.disabled || props.loading)}
      />
    ) : null
)

export const Button = forwardRef<
  HTMLButtonElement | HTMLAnchorElement,
  ButtonProps
>(({ customPriority, ...props }, ref) => {
  return (
    <ButtonDSFR
      {...props}
      iconId={props.loading ? "ri-loader-line" : props.iconId}
      className={cl(props.className, {
        [css["button-danger"] as string]: customPriority === "danger",
        [css["button-success"] as string]: customPriority === "success",
        [css["button-as-link-style"] as string]: customPriority === "link",
      })}
      priority={
        customPriority && ["danger", "success"].includes(customPriority)
          ? "tertiary"
          : props.priority
      }
      {...layout(props)}
      // @ts-ignore couldn't find a better way to manage different cases for button (anchor, button, icon only)
      ref={ref}
    />
  )
})
