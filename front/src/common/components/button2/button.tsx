import {
  Button as ButtonDSFR,
  ButtonProps as ButtonDSFRProps,
} from "@codegouvfr/react-dsfr/Button"
import { ForwardedRef, forwardRef } from "react"
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
  if (customPriority === "link") {
    return (
      <BaseButton
        {...props}
        ref={ref as ForwardedRef<HTMLButtonElement>}
        className={cl(props.className, css["button-as-link-style"])}
        {...layout(props)}
      >
        {props.children}
      </BaseButton>
    )
  }

  const baseProps = {
    className: cl(props.className, {
      [css["button-danger"]]: customPriority === "danger",
      [css["button-success"]]: customPriority === "success",
    }),
  }

  return props.linkProps ? (
    <ButtonDSFR
      {...baseProps}
      {...props}
      {...layout(props)}
      ref={ref as ForwardedRef<HTMLAnchorElement>}
    />
  ) : // Couldn't find a better way to specify the iconId for the loading state
  props.iconId ? (
    <BaseButton
      {...baseProps}
      {...props}
      iconId={props.loading ? "ri-loader-line" : props.iconId}
    />
  ) : (
    <BaseButton {...baseProps} {...props} />
  )
})
