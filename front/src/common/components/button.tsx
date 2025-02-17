import cl from "clsx"
import { Loader, Upload } from "common/components/icons"
import css from "./button.module.css"
import { Layout, layout } from "./scaffold"
import { Link, To } from "react-router-dom"

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
  autoFocus?: boolean
  className?: string
  style?: React.CSSProperties
  children?: React.ReactNode
  domRef?: React.RefObject<HTMLButtonElement>
  disabled?: boolean
  loading?: boolean
  captive?: boolean
  center?: boolean
  variant?: ButtonVariant
  label?: string
  title?: string
  icon?: React.ReactNode | React.ComponentType
  submit?: string | boolean
  tabIndex?: number
  href?: string
  to?: To
  action?: (() => T) | (() => Promise<T>)
}

export function Button<T>({
  className,
  style,
  children,
  domRef,
  autoFocus,
  disabled,
  loading,
  captive,
  variant,
  label,
  title,
  icon: Icon,
  submit,
  tabIndex,
  href,
  to,
  center,
  action,
  ...props
}: ButtonProps<T>) {
  const icon = typeof Icon === "function" ? <Icon /> : Icon
  const hasIconAndText = Boolean(Icon) && Boolean(label || children)

  const content = label ?? children

  return (
    <LinkWrapper href={href} to={to} {...props}>
      <button
        ref={domRef}
        {...layout(props)}
        autoFocus={autoFocus}
        data-captive={captive ? true : undefined}
        tabIndex={tabIndex}
        disabled={disabled || loading}
        type={submit ? "submit" : "button"}
        form={typeof submit === "string" ? submit : undefined}
        title={title}
        style={style}
        className={cl(
          css.button,
          variant,
          variant && css[variant],
          center && css.center,
          hasIconAndText && css.composite,
          className
        )}
        onClick={(e) => {
          if (captive) {
            e.stopPropagation()
            e.preventDefault()
          }
          action?.()
        }}
      >
        {loading ? <Loader /> : icon}
        {variant !== "icon" && (center ? <span>{content}</span> : content)}
      </button>
    </LinkWrapper>
  )
}

interface LinkWrapperProps extends Layout {
  href?: string
  to?: To
  children: React.ReactNode
}

const LinkWrapper = ({ href, to, children, ...props }: LinkWrapperProps) => {
  if (href) {
    return (
      <a href={href} className={css.wrapper} {...layout(props)}>
        {children}
      </a>
    )
  } else if (to) {
    return (
      <Link to={to} className={css.wrapper} {...layout(props)}>
        {children}
      </Link>
    )
  } else {
    return <>{children}</>
  }
}

interface ExternalLinkProps {
  to?: To
  href?: string
  className?: string
  children?: React.ReactNode
}

export const ExternalLink = ({
  className,
  children,
  to,
  href,
}: ExternalLinkProps) => {
  const props = {
    className: cl(css.external, className),
    children: <>{children}</>,
  }

  if (to !== undefined) {
    return <Link {...props} to={to} />
  } else if (href !== undefined) {
    // eslint-disable-next-line
    return <a {...props} href={href} target="_blank" rel="noreferrer" />
  } else {
    throw new Error("Missing url in external link")
  }
}

export type MailtoProps = JSX.IntrinsicElements["a"] & {
  user: string
  host: string
  subject?: string
  body?: string
}

export const MailTo = ({
  user,
  host,
  className,
  children,
  subject,
  body, //use https://mailtolink.me/ to convert body message
  ...props
}: MailtoProps) => {
  let href = `mailto:${user}@${host}`
  href += `?subject=${subject ? encodeURIComponent(subject) : ""}`
  href += `&body=${body || ""}`
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className={cl(css.mailto, className)}
      {...props}
    >
      {children}
    </a>
  )
}

export const DownloadLink = ({
  href: url,
  label,
}: {
  href: string
  label: string
}) => (
  <a
    href={url ?? "#"}
    className={css.downloadLink}
    target="_blank"
    rel="noreferrer"
  >
    <Upload />
    {label}
  </a>
)

export default Button
