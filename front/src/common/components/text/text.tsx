/**
 * Text component based on the French Government Design System (DSFR)
 * Implements typography styles defined in:
 * @see https://www.systeme-de-design.gouv.fr/fondamentaux/typographie
 */

type TextProps = {
  // The tag to use for the text
  is?: React.ElementType

  // The content of the text
  children: React.ReactNode

  size?: "sm" | "md" | "lg" | "xl"
}
export const Text = ({ is = "p", children, size = "md" }: TextProps) => {
  const TextTag = is

  return <TextTag className="">{children}</TextTag>
}
