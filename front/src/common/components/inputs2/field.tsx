import { fr } from "@codegouvfr/react-dsfr"
import { InputProps } from "@codegouvfr/react-dsfr/Input"
import { ReactNode, useId } from "react"
import cl from "clsx"
import css from "./field.module.css"

export type FieldProps = {
  children: ReactNode
} & Omit<InputProps, "children" | "nativeSelectProps">

export const Field = ({
  children,
  label,
  hintText,
  id: idProps,
  state = "default",
  stateRelatedMessage,
  className,
  disabled,
}: FieldProps) => {
  const generatedId = useId()
  const selectId = idProps ?? generatedId

  const stateClass = {
    success: fr.cx("fr-valid-text"),
    error: fr.cx("fr-error-text"),
    info: fr.cx("fr-info-text"),
  }
  return (
    <div
      className={cl(
        fr.cx("fr-select-group"),
        className,
        disabled && "fr-select-group--disabled",
        state !== "default" && `fr-select-group--${state}`
      )}
    >
      {Boolean(label || hintText) && (
        <label className={fr.cx("fr-label")} htmlFor={selectId}>
          {label}
          {hintText !== undefined && (
            <span className={fr.cx("fr-hint-text")}>{hintText}</span>
          )}
        </label>
      )}
      <div className={css["select-field-children"]}>{children}</div>
      {state !== "default" && (
        <p id={`${selectId}-desc`} className={stateClass[state]}>
          {stateRelatedMessage}
        </p>
      )}
    </div>
  )
}
