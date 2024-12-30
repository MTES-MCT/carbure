import React, { ReactNode } from "react"
import cl from "clsx"
import css from "./dialog.module.css"
import { Overlay } from "../scaffold"
import { Button } from "../button2"
import { ButtonVariant } from "../button"
import { Title, TitleProps } from "../title"
import { Text, TextProps } from "../text"

export interface DialogProps {
  className?: string
  style?: React.CSSProperties
  fullscreen?: boolean
  children: React.ReactNode
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
      >
        Fermer
      </Button>
      {header && <header className={css["dialog__header"]}>{header}</header>}
      <main>{children}</main>
      {footer && <footer>{footer}</footer>}
    </div>
  </div>
)

export interface ConfirmProps {
  title: string
  description: ReactNode
  confirm: string
  variant: ButtonVariant
  icon?: React.ComponentType | React.ElementType
  onConfirm: () => Promise<any>
  onClose: () => void
}

// export const Confirm = ({
//   title,
//   description,
//   confirm,
//   variant,
//   icon = Check,
//   onConfirm,
//   onClose,
// }: ConfirmProps) => {
//   const { t } = useTranslation()
//   const confirmAction = useMutation(onConfirm)
//   return (
//     <Dialog onClose={onClose}>
//       <header>
//         <h1>{title}</h1>
//       </header>
//       <main>
//         <section>{description}</section>
//       </main>
//       <footer>
//         <Button
//           asideX
//           autoFocus
//           icon={icon}
//           variant={variant}
//           label={confirm}
//           loading={confirmAction.loading}
//           action={() => confirmAction.execute().then(onClose)}
//         />
//         <Button icon={Return} label={t("Annuler")} action={onClose} />
//       </footer>
//     </Dialog>
//   )
// }

const DialogTitle = (props: Omit<TitleProps, "is" | "as">) => (
  <Title is="h2" as="h5" className={css["dialog__title"]} {...props} />
)

const DialogDescription = <T extends React.ElementType>(
  props: Omit<TextProps<T>, "size">
) => <Text size="sm" {...props} />

Dialog.Title = DialogTitle
Dialog.Description = DialogDescription

export default Dialog
