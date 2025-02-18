import { Accordion, AccordionProps } from "@codegouvfr/react-dsfr/Accordion"
import { Icon, IconName } from "common/components/icon"

export type CollapseProps = AccordionProps & {
  icon?: IconName
}

export const Collapse = ({ icon, label, children }: CollapseProps) => {
  return (
    <Accordion
      label={
        <>
          {icon && (
            <Icon name={icon} style={{ marginRight: "var(--spacing-1w)" }} />
          )}
          {label}
        </>
      }
    >
      {children}
    </Accordion>
  )
}
