/**
 * This component is a wrapper around the DSFR notice component.
 * However, the react component exposed by @codegouvfr/react-dsfr is not fully
 * compatible with the DSFR CSS.
 * This is why we are using the native HTML element and only style it with CSS.
 */
import { useState } from "react"
import cl from "clsx"
import css from "./notice.module.css"
import { fr } from "@codegouvfr/react-dsfr"
import { IconProps } from "../icon"
import { NavLink } from "../nav-link"

type CustomRenderer = (config: { close: () => void }) => React.ReactNode
export type NoticeVariant = "info" | "warning" | "alert"

export interface NoticeProps {
  variant?: NoticeVariant
  icon?: React.ComponentType<IconProps>
  title?: string
  children?: React.ReactNode | CustomRenderer

  style?: React.CSSProperties
  className?: string
  isClosable?: boolean
  onClose?: () => void

  // The text displayed in the link
  linkText?: string

  // The URL of the link. If provided, a link will be displayed in the notice. If not, a button triggers the action event.
  linkHref?: string

  // Event triggered when the user clicks on the link
  onAction?: () => void
}

export const Notice = ({
  variant,
  icon: Icon,
  title,
  children,
  className,
  style,
  isClosable,
  onClose,
  linkText,
  linkHref,
  onAction,
}: NoticeProps) => {
  const [open, setOpen] = useState(true)

  if (!open) return null

  const config = {
    close: () => setOpen(false),
  }

  const child = typeof children === "function" ? children(config) : children

  const handleClose = () => {
    setOpen(false)
    onClose?.()
  }

  return (
    <div
      className={cl(
        fr.cx("fr-notice"),
        variant && fr.cx(`fr-notice--${variant}`),
        className
      )}
      style={style}
    >
      <div className="fr-container">
        <div className="fr-notice__body">
          <p>
            {Icon && <Icon size="md" className={css.notice__icon} />}
            <span className={cl(fr.cx("fr-notice__title"), css.notice__title)}>
              {title}
            </span>
            {child && (
              <span className={cl(fr.cx("fr-notice__desc"), css.notice__desc)}>
                {child}
              </span>
            )}
            {linkText && linkHref && (
              <NavLink
                to={linkHref}
                className={fr.cx("fr-notice__link")}
                underline
              >
                {linkText}
              </NavLink>
            )}
            {linkText && onAction && (
              <button className={css.notice__link} onClick={onAction}>
                {linkText}
              </button>
            )}
          </p>
          {isClosable && (
            <button
              className={cl(fr.cx("fr-btn"), fr.cx("fr-btn--close"))}
              onClick={handleClose}
            ></button>
          )}
        </div>
      </div>
    </div>
  )
}
