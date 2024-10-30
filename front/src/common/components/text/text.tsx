/**
 * Text component based on the French Government Design System (DSFR)
 * Implements typography styles defined in:
 * @see https://www.systeme-de-design.gouv.fr/fondamentaux/typographie
 */

import { fr } from "@codegouvfr/react-dsfr"
import cl from "clsx"
import styles from "./text.module.css"

type TextOwnProps<T extends React.ElementType> = {
  // The HTML tag to use for the text
  is?: T

  // The content of the text
  children: React.ReactNode

  // The size of the text
  size?: "xs" | "sm" | "md" | "lg" | "xl"

  // Additional CSS classes
  className?: string
  style?: React.CSSProperties

  // Add/remove the border bottom defined in the DSFR
  margin?: boolean

  fontWeight?: "light" | "regular" | "semibold" | "bold" | "heavy"
}

// Make mandatory the componentProps property if there are mandatory props for the generic component
type TextProps<T extends React.ElementType> = TextOwnProps<T> &
  (object extends React.ComponentProps<T>
    ? { componentProps?: React.ComponentProps<T> }
    : { componentProps: React.ComponentProps<T> })

const defaultElement = "p"

export const Text: <T extends React.ElementType = typeof defaultElement>(
  props: TextProps<T>
) => React.ReactElement | null = ({
  is: TextTag = defaultElement,
  children,
  size = "md",
  className,
  margin = false,
  fontWeight = "regular",
  componentProps,
  ...props
}) => {
  return (
    <TextTag
      {...componentProps}
      className={cl(
        fr.cx(`fr-text--${size}`),
        !margin && styles.noMargin,
        fontWeight === "semibold"
          ? styles.semibold
          : fr.cx(`fr-text--${fontWeight}`),
        className,
        componentProps?.className
      )}
      {...props}
    >
      {children}
    </TextTag>
  )
}
