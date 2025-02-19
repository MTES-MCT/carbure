import cl from "clsx"
import { Loader } from "./icons"
import css from "./scaffold.module.css"

// top bar for the whole website, horizontal flow
export const Header = (props: JSX.IntrinsicElements["header"]) => (
  <header {...props} className={cl(css.header, props.className)} />
)

// main content of the current page, vertical flow, can have a <header> and many <section>
export const Main = (props: JSX.IntrinsicElements["main"]) => (
  <main {...props} className={cl(css.main, props.className)} />
)

// a div used inside Main component to remove the padding and set a background color
export const Content = ({
  marginTop,
  ...props
}: JSX.IntrinsicElements["div"] & { marginTop?: boolean }) => (
  <div
    {...props}
    className={cl(
      css.content,
      props.className,
      marginTop && css["content--margin-top"]
    )}
  />
)

// bottom footer with links and info, divided into some vertical <section>
export const Footer = (props: JSX.IntrinsicElements["footer"]) => (
  <footer {...props} className={cl(css.footer, props.className)} />
)

// a special bar to put inside a Main to differentiate it from the rest of the content
export const Bar = (props: JSX.IntrinsicElements["section"]) => (
  <section {...props} className={cl(css.bar, props.className)} />
)

// a div that grows to fill the available space (used in ActionBar)
const ActionBarGrow = (props: JSX.IntrinsicElements["div"]) => (
  <div {...props} className={css["actionbar--grow"]} />
)

// a bar where you can put many buttons
export const ActionBar = ({ ...props }: JSX.IntrinsicElements["section"]) => (
  <section {...props} className={cl(css.actionbar, props.className)} />
)

ActionBar.Grow = ActionBarGrow

// a enclosed box with its own <header>, many <section> and <footer>
export const Panel = ({
  id,
  children,
  ...props
}: JSX.IntrinsicElements["article"]) => (
  <article {...props} className={cl(css.panel, props.className)}>
    {id && <div id={id} className={css.anchor} />}
    {children}
  </article>
)

// a container that automatically arranges its content into a grid
export const Grid = (props: JSX.IntrinsicElements["div"]) => (
  <div {...props} className={cl(css.grid, props.className)} />
)

// a div with vertical flow
export const Col = ({
  asideX,
  asideY,
  className,
  grow,
  gap,
  ...props
}: JSX.IntrinsicElements["div"] & Layout & { grow?: boolean; gap?: "md" }) => (
  <div
    {...props}
    {...layout({ asideX, asideY })}
    className={cl(
      css.column,
      grow && css["column--grow"],
      gap && css[`column--gap-${gap}`],
      className
    )}
  />
)

// a div with horizontal flow
export const Row = ({
  asideX,
  asideY,
  className,
  ...props
}: JSX.IntrinsicElements["div"] & Layout) => (
  <div
    {...props}
    {...layout({ asideX, asideY })}
    className={cl(css.row, className)}
  />
)

export const Overlay = (props: JSX.IntrinsicElements["div"]) => (
  <div {...props} className={cl(css.overlay, props.className)} />
)

export const LoaderOverlay = () => (
  <Overlay className={css.loaderOverlay}>
    <Loader color="var(--black)" size={32} />
  </Overlay>
)

export const Divider = (props: JSX.IntrinsicElements["div"]) => (
  <div {...props} className={cl(css.divider, props.className)} />
)

export interface Layout {
  asideX?: boolean
  asideY?: boolean
  spread?: boolean
}

export function layout(props: Layout) {
  return {
    "data-asidex": props.asideX ? true : undefined,
    "data-asidey": props.asideY ? true : undefined,
    "data-spread": props.spread ? true : undefined,
  }
}
