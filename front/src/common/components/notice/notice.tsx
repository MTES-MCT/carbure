/**
 * This component is a wrapper around the DSFR notice component.
 * However, the react component exposed by @codegouvfr/react-dsfr is not fully
 * compatible with the DSFR CSS.
 * This is why we are using the native HTML element and only style it with CSS.
 */
import { useState } from "react"
import cl from "clsx"
import css from "./notice.module.css"
import { IconProps } from "../icon"
import { Button } from "../button2"

type CustomRenderer = (config: { close: () => void }) => React.ReactNode
export type NoticeVariant = "info" | "warning" | "alert"

export interface NoticeProps {
  variant?: NoticeVariant
  icon?: React.ComponentType<IconProps> | null
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

  noColor?: boolean
}

export const Notice = ({
  variant = "info",
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
  noColor,
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
        variant && css[`notice--${variant}`],
        className,
        css["notice"],
        noColor && css["notice--no-color"]
      )}
      style={style}
    >
      <div className={css.notice__body}>
        <div>
          {Icon ? <Icon size="md" className={css.notice__icon} /> : null}
          {title && (
            <span className={css.notice__title}>
              <strong>{title}</strong>
            </span>
          )}
          {child}
          {linkText && linkHref && (
            <Button
              customPriority="link"
              linkProps={{ to: linkHref }}
              className={css["notice__link"]}
            >
              {linkText}
            </Button>
          )}
          {linkText && onAction && (
            <Button
              customPriority="link"
              onClick={onAction}
              className={css["notice__link"]}
            >
              {linkText}
            </Button>
          )}
        </div>
        {isClosable && (
          <Button
            iconId="fr-icon-close-line"
            onClick={handleClose}
            title="Close"
            priority="tertiary no outline"
            size="small"
            className={css["notice__close"]}
          />
        )}
      </div>
    </div>
  )
}
