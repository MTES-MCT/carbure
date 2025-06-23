import { useRef } from "react"
import { Label } from "../base-input"
import { useTranslation } from "react-i18next"
import css from "./base-file-input.module.css"
import cl from "clsx"
import { Field, FieldProps } from "../field"
import i18next from "i18next"
import { fr } from "@codegouvfr/react-dsfr"
import { Icon } from "common/components/icon"
import { Ellipsis } from "common/components/scaffold"

export type BaseFileInputProps = Omit<FieldProps, "children"> & {
  value?: File | FileList
  onChange?: (e?: React.ChangeEvent<HTMLInputElement>) => void
  multiple?: boolean
}

export const BaseFileInput = ({
  required,
  onChange,
  autoFocus,
  disabled,
  readOnly,
  multiple,
  name,
  placeholder = i18next.t("Selectionner un fichier"),
  hasTooltip,
  title,
  label,
  ...props
}: BaseFileInputProps) => {
  const { t } = useTranslation()
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!inputRef.current) return
    const files = e.target.files

    if (files === null) return

    for (const file of files) {
      if (file.size > 5000000) {
        const message = t(
          'La taille du fichier "{{fileName}}" est trop importante pour être analysée (5mo maximum).',
          { fileName: file.name }
        )
        inputRef.current.setCustomValidity(message)
        inputRef.current.reportValidity()
        return
      }
    }

    return onChange?.(e)
  }

  return (
    <Field
      {...props}
      label={
        <Label
          hasTooltip={hasTooltip}
          required={required}
          title={title}
          label={label}
        />
      }
    >
      <label className={cl(css["base-file-input__label"], fr.cx("fr-input"))}>
        <input
          ref={inputRef}
          autoFocus={autoFocus}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          multiple={multiple}
          name={name}
          style={{ opacity: 0, position: "absolute" }}
          type="file"
          onChange={handleChange}
        />
        <Ellipsis maxWidth="100%">{placeholder}</Ellipsis>
        <Icon
          name={props.value ? "ri-check-line" : "ri-upload-2-line"}
          asideX
          size="sm"
        />
      </label>
    </Field>
  )
}
