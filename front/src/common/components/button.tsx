import cl from "clsx"
import { Loader, Upload } from "common/components/icons"
import css from "./button.module.css"
import { Layout, layout } from "./scaffold"
import { Link } from "react-router-dom"
import { ExternalLink as ExternalLinkIcon } from "common/components/icons"

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
  autoFocus,
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
  center,
  action,
}: ButtonProps<T>) {
  const icon = typeof Icon === "function" ? <Icon /> : Icon
  const hasIconAndText = Boolean(Icon) && Boolean(label || children)

  const content = label ?? children

  return (
    <LinkWrapper href={href} to={to}>
      <button
        ref={domRef}
        {...layout({ asideX, asideY, spread })}
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
          captive && e.stopPropagation()
          captive && e.preventDefault()
          action?.()
        }}
      >
        {loading ? <Loader /> : icon}
        {variant !== "icon" && (center ? <span>{content}</span> : content)}
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

interface ExternalLinkProps {
  to?: string
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
    children: (
      <>
        {children}
        <ExternalLinkIcon size={20} />
      </>
    ),
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
}

export const MailTo = ({
  user,
  host,
  className,
  children,
  ...props
}: MailtoProps) => (
  <a
    href={`mailto:${user}@${host}`}
    target="_blank"
    rel="noreferrer"
    className={cl(css.mailto, className)}
    {...props}
  >
    {children}
  </a>
)

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
