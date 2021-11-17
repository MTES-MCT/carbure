import cl from "clsx"
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
}

export function Button<T>({
  className,
  style,
  children,
  domRef,
  disabled,
  loading,
  asideX,
  asideY,
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
}: ButtonProps<T>) {
  const icon = typeof Icon === "function" ? <Icon /> : Icon
  const hasIconAndText = Boolean(Icon) && Boolean(label || children)

  return (
    <LinkWrapper href={href} to={to}>
      <button
        ref={domRef}
        {...layout({ asideX, asideY, spread })}
        data-captive={captive ? true : undefined}
        tabIndex={tabIndex}
        disabled={disabled || loading}
        type={submit ? "submit" : "button"}
        form={typeof submit === "string" ? submit : undefined}
        title={title}
        style={style}
        className={cl(
          css.button,
          variant && css[variant],
          hasIconAndText && css.composite,
          className
        )}
        onClick={(e) => {
          captive && e.stopPropagation()
          action?.()
        }}
      >
        {loading ? <Loader /> : icon}
        {variant !== "icon" && (label ?? children)}
      </button>
    </LinkWrapper>
  )
}

interface LinkWrapperProps {
  href?: string
  to?: string
  children: React.ReactNode
}

const LinkWrapper = ({ href, to, children }: LinkWrapperProps) => {
  if (href) {
    return (
      <a href={href} className={css.wrapper}>
        {children}
      </a>
    )
  } else if (to) {
    return (
      <Link to={to} className={css.wrapper}>
        {children}
      </Link>
    )
  } else {
    return <>{children}</>
  }
}

export default Button
