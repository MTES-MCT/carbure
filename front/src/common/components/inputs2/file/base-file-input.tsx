import { forwardRef, useRef } from "react"
import { ExtendedInputProps, Label } from "../base-input"
import { Upload, UploadProps } from "@codegouvfr/react-dsfr/Upload"
import { useTranslation } from "react-i18next"

export type BaseFileInputProps = UploadProps &
  ExtendedInputProps & {
    value?: File | FileList
    onChange?: (e?: React.ChangeEvent<HTMLInputElement>) => void
    multiple?: boolean
  }

export const BaseFileInput = forwardRef<HTMLDivElement, BaseFileInputProps>(
  (
    {
      hasTooltip,
      required,
      title,
      label,
      onChange,
      autoFocus,
      disabled,
      readOnly,
      multiple,
      name,
      ...props
    },
    ref
  ) => {
    const { t } = useTranslation()
    const inputRef = useRef<HTMLInputElement>(null)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!inputRef.current) return
      const files = e.target.files

      if (files === null) return

      for (const file of files) {
        console.log("taille du fichier", file.size)
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
      <Upload
        {...props}
        label={
          <Label
            hasTooltip={hasTooltip}
            required={required}
            title={title}
            label={label}
          />
        }
        ref={ref}
        nativeInputProps={{
          ...props.nativeInputProps,
          onChange: handleChange,
          required,
          autoFocus,
          disabled,
          readOnly,
          multiple,
          name,
          ref: inputRef,
        }}
      />
    )
  }
)
