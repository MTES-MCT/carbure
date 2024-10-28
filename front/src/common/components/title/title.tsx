/**
 * Title component based on the French Government Design System (DSFR)
 * Implements typography styles defined in:
 * @see https://www.systeme-de-design.gouv.fr/fondamentaux/typographie
 */

import cl from "clsx"
import styles from "./title.module.css"
type HeadingTags = "h1" | "h2" | "h3" | "h4" | "h5" | "h6"
type TitleProps = {
  // The tag to use for the title
  is: React.ElementType

  // The content of the title
  children: React.ReactNode

  // Property used to override the visual style of a heading tag
  // Example: <Title is="h1" as="h3"> will render an h1 with h3 visual style
  // Note: This property only works when "is" is a heading tag (h1-h6)
  as?: HeadingTags

  // If the default style is not appropriate, you can override it with this property
  size?: "xs" | "sm" | "md" | "lg" | "xl"

  className?: string

  style?: React.CSSProperties

  border?: boolean
}

export const Title = ({
  is,
  children,
  as,
  size,
  border = false,
  className,
  ...props
}: TitleProps) => {
  const TitleTag = is
  const classes = cl(
    as && `fr-${as}`,
    size && `fr-display--${size}`,
    !border && styles.title,
    className
  )

  return (
    <TitleTag className={classes} {...props}>
      {children}
    </TitleTag>
  )
}
