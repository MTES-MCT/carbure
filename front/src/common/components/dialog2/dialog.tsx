import React, { ReactNode } from "react"
import cl from "clsx"
import css from "./dialog.module.css"
import { Overlay } from "../scaffold"
import { Button, ButtonProps } from "../button2"
import { Title, TitleProps } from "../title"
import { Text, TextProps } from "../text"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { IconName } from "../icon"

export interface DialogProps {
  className?: string
  style?: React.CSSProperties
  fullscreen?: boolean
  children?: React.ReactNode
  header?: React.ReactNode
  footer?: React.ReactNode
  onClose: () => void
}

export const Dialog = ({
  className,
  style,
  children,
  header,
  footer,
  fullscreen,
  onClose,
}: DialogProps) => (
  <div className={css.screen}>
    <Overlay onClick={onClose} />
    <div
      className={cl(css.dialog, fullscreen && css.fullscreen, className)}
      style={style}
    >
      <Button
        priority="tertiary no outline"
        iconId="fr-icon-close-line"
        iconPosition="right"
        asideX
        size="small"
        onClick={onClose}
        className={css["dialog__close-button"]}
      >
        Fermer
      </Button>
      <div className={css["dialog__wrapper"]}>
        {header && <header className={css["dialog__header"]}>{header}</header>}
        <main>{children}</main>
        {footer && <footer className={css["dialog__footer"]}>{footer}</footer>}
      </div>
    </div>
  </div>
)

const DialogTitle = (props: Omit<TitleProps, "is" | "as">) => (
  <Title is="h2" as="h5" className={css["dialog__title"]} {...props} />
)

const DialogDescription = <T extends React.ElementType>(
  props: Omit<TextProps<T>, "size">
) => <Text size="sm" {...props} />

Dialog.Title = DialogTitle
Dialog.Description = DialogDescription

export default Dialog

export interface ConfirmProps {
  title: string
  description: ReactNode
  confirm: string
  variant?: ButtonProps["priority"]
  icon?: IconName
  onConfirm: () => Promise<any>
  onClose: () => void
}
export const Confirm = ({
  title,
  description,
  confirm,
  variant = "primary",
  icon,
  onConfirm,
  onClose,
}: ConfirmProps) => {
  const { t } = useTranslation()
  const confirmAction = useMutation(onConfirm)
  const commonButtonProps = {
    nativeButtonProps: { autoFocus: true },
    priority: variant,
    loading: confirmAction.loading,
    onClick: () => confirmAction.execute().then(onClose),
  }
  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </>
      }
      footer={
        <>
          <Button priority="secondary">{t("Annuler")}</Button>
          {/* Couldn't find a better way to handle icon prop drilling */}
          {icon ? (
            <Button {...commonButtonProps} iconId={icon}>
              {confirm}
            </Button>
          ) : (
            <Button {...commonButtonProps}>{confirm}</Button>
          )}
        </>
      }
    ></Dialog>
  )
}