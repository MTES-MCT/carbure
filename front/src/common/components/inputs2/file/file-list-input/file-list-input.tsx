import { BaseFileInput, BaseFileInputProps } from "../base-file-input"

export type FileListInputProps = Omit<
  BaseFileInputProps,
  "nativeInputProps" | "multiple"
> & {
  value?: FileList
  onChange?: (value: FileList | undefined) => void
}

export const FileListInput = ({ onChange, ...props }: FileListInputProps) => {
  return (
    <BaseFileInput
      {...props}
      onChange={
        onChange ? (e) => onChange(e?.target.files ?? undefined) : undefined
      }
      multiple
    />
  )
}
