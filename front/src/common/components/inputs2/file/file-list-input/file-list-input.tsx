import { BaseFileInput, BaseFileInputProps } from "../base-file-input"

export type FileListInputProps = Omit<
  BaseFileInputProps,
  "nativeInputProps" | "multiple" | "onChange" | "value"
> & {
  value?: FileList
  onChange?: (value: FileList | undefined) => void
}

export const FileListInput = ({
  onChange,
  value,
  placeholder,
  ...props
}: FileListInputProps) => {
  return (
    <BaseFileInput
      {...props}
      value={value}
      onChange={
        onChange ? (e) => onChange(e?.target.files ?? undefined) : undefined
      }
      multiple
      placeholder={value?.[0]?.name ?? placeholder}
    />
  )
}
