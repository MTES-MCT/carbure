import React, { CSSProperties } from "react"
import cl from "clsx"

import styles from "./index.module.css"

import { Loader } from "./icons"

export type SystemProps = {
  className?: string
  style?: CSSProperties
  children?: React.ReactNode
}

export type AsProp = {
  as?: string | React.ComponentType<any>
}

export type BoxProps = SystemProps &
  React.HTMLProps<HTMLDivElement> & {
    row?: boolean
    as?: string | React.ComponentType<any>
  }

export const Box = ({
  row = false,
  as: Component = "div",
  className,
  children,
  ...props
}: BoxProps) => (
  <Component
    {...props}
    className={cl(styles.box, row && styles.boxRow, className)}
  >
    {children}
  </Component>
)

export const Main = (props: BoxProps) => <Box {...props} as="main" />

// TITLE COMPONENT

type TitleProps = SystemProps & React.HTMLProps<HTMLHeadingElement>

export const Title = ({ children, className, ...props }: TitleProps) => (
  <h1 {...props} className={cl(styles.title, className)}>
    {children}
  </h1>
)

// LOADER OVERLAY

export const LoaderOverlay = () => (
  <Box className={styles.loaderOverlay}>
    <Loader color="var(--black)" size={48} title="Chargement..." />
  </Box>
)
