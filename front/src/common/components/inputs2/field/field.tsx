import { fr } from "@codegouvfr/react-dsfr"
import { ReactNode, useId } from "react"
import cl from "clsx"
import css from "./field.module.css"
import { InputProps } from "common/components/inputs2/input"

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
  marginBottom = false,
  required,
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
        fr.cx("fr-input-group"),
        className,
        disabled && "fr-input-group--disabled",
        !marginBottom && css["no-margin-bottom"]
      )}
    >
      {Boolean(label || hintText) && (
        <label className={fr.cx("fr-label")} htmlFor={selectId}>
          {label} {required && "*"}
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
