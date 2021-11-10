import cl from "clsx"
import { Fragment, useEffect, useState } from "react"
import { Loader } from "./icons"
import css from "./button.module.css"
import { Layout, layout } from "./scaffold"
import { Link } from "react-router-dom"

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "success"
  | "warning"
  | "danger"
  | "text"
  | "link"
  | "icon"

export interface ButtonProps<T = void> extends Layout {
  className?: string
  style?: React.CSSProperties
  children?: React.ReactNode
  domRef?: React.RefObject<HTMLButtonElement>
  disabled?: boolean
  loading?: boolean
  captive?: boolean
  variant?: ButtonVariant
  label?: string
  title?: string
  icon?: React.ReactNode | (() => React.ReactNode)
  submit?: string | boolean
  tabIndex?: number
  href?: string
  to?: string
  action?: (() => T) | (() => Promise<T>)
  dialog?: (close: () => void) => React.ReactNode
  onSuccess?: (result: T) => void
  onError?: (error: unknown) => void
}

export function Button<T>({
  className,
  style,
  children,
  domRef,
  disabled,
  loading,
  aside,
  spread,
  captive,
  variant,
  label,
  title,
  icon: Icon,
  submit,
  tabIndex,
  href,
  to,
  action,
  dialog,
  onSuccess,
  onError,
}: ButtonProps<T>) {
  const [active, showDialog] = useState(false)

  const icon = typeof Icon === "function" ? <Icon /> : Icon
  const hasIconAndText = Boolean(Icon) && Boolean(label || children)

  // prettier-ignore
  const openDialog = dialog
    ? () => showDialog(true)
    : undefined;

  const runAction = action
    ? () => handle(action, { onSuccess, onError })
    : undefined

  return (
    <>
      <LinkWrapper href={href} to={to}>
        <button
          ref={domRef}
          {...layout({ aside, spread })}
          data-captive={captive ? true : undefined}
          tabIndex={tabIndex}
          disabled={disabled || loading}
          type={submit ? "submit" : "button"}
          title={title}
          style={style}
          className={cl(
            css.button,
            variant && css[variant],
            hasIconAndText && css.composite,
            className
          )}
          onClick={openDialog ?? runAction}
        >
          {loading ? <Loader /> : icon}
          {variant !== "icon" && (label ?? children)}
        </button>
      </LinkWrapper>

      {active && dialog?.(() => showDialog(false))}
    </>
  )
}

type Action<T = void> = (() => T) | (() => Promise<T>)

interface Handlers<T> {
  onSuccess?: (result: T) => void
  onError?: (error: unknown) => void
}

async function handle<T>(action: Action<T>, handlers: Handlers<T>) {
  try {
    const result = await action()
    handlers.onSuccess?.(result)
  } catch (error) {
    handlers.onError?.(error)
  }
}

interface LinkWrapperProps {
  href?: string
  to?: string
  children: React.ReactNode
}

const LinkWrapper = ({ href, to, children }: LinkWrapperProps) => {
  if (href) {
    return <a href={href}>{children}</a>
  } else if (to) {
    return <Link to={to}>{children}</Link>
  } else {
    return <>{children}</>
  }
}

export default Button
