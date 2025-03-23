import { Accordion, AccordionProps } from "@codegouvfr/react-dsfr/Accordion"
import { Icon, IconName } from "common/components/icon"
import css from "./collapse.module.css"
import cl from "clsx"

export type CollapseProps = AccordionProps & {
  icon?: IconName
}

export const Collapse = ({
  icon,
  label,
  children,
  ...props
}: CollapseProps) => {
  return (
    <Accordion
      {...props}
      label={
        <>
          {icon && (
            <Icon name={icon} style={{ marginRight: "var(--spacing-1w)" }} />
          )}
          {label}
        </>
      }
      className={cl(css.collapse, props.className)}
    >
      {children}
    </Accordion>
  )
}
