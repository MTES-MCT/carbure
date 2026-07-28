import css from "./container.module.css"
import cl from "clsx"
import { Dialog, DialogProps } from "common/components/dialog2"
import { Title } from "common/components/title"
import { ReactNode } from "react"

export const DialogContainerSpacing = () => {
  return <div style={{ marginBottom: "var(--spacing-6w)" }} />
}
export const DialogContainer = (props: DialogProps & { title?: ReactNode }) => {
  return (
    <Dialog {...props} className={css["dialog-container"]}>
      {props.title && (
        <Title is="h2" as="h4">
          {props.title}
        </Title>
      )}
      {props.children}
    </Dialog>
  )
}

export const Container = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className={css.container}>
      <div className={css["container-content"]}>{children}</div>
    </div>
  )
}

export const FooterAuth = ({
  children,
  asideX,
}: {
  children: React.ReactNode
  asideX?: boolean
}) => {
  return (
    <footer
      className={cl(css["footer-auth"], asideX && css["footer-auth--aside-x"])}
    >
      {children}
    </footer>
  )
}

// Separate content like form and footer with a large gap
export const Content = ({ children }: { children: React.ReactNode }) => {
  return <div className={css.content}>{children}</div>
}

// Separate elements with a small gap between them
export const Section = ({
  children,
  gap = "md",
}: {
  children: React.ReactNode
  gap?: "md" | "lg"
}) => {
  return (
    <section className={cl(css.section, gap && css[`section--gap-${gap}`])}>
      {children}
    </section>
  )
}
