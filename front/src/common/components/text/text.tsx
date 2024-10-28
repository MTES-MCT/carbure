/**
 * Text component based on the French Government Design System (DSFR)
 * Implements typography styles defined in:
 * @see https://www.systeme-de-design.gouv.fr/fondamentaux/typographie
 */

import { fr } from "@codegouvfr/react-dsfr"
import cl from "clsx"
import styles from "./text.module.css"
type TextProps = {
  // The tag to use for the text
  is?: React.ElementType

  // The content of the text
  children: React.ReactNode

  size?: "xs" | "sm" | "md" | "lg" | "xl"

  className?: string

  style?: React.CSSProperties

  border?: boolean
}
export const Text = ({
  is = "p",
  children,
  size = "md",
  className,
  border = false,
  ...props
}: TextProps) => {
  const TextTag = is

  return (
    <TextTag
      className={cl(
        fr.cx(`fr-text--${size}`),
        !border && styles.text,
        className
      )}
      {...props}
    >
      {children}
    </TextTag>
  )
}
