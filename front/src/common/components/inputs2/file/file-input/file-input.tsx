import { BaseFileInput, BaseFileInputProps } from "../base-file-input"

export type FileInputProps = Omit<
  BaseFileInputProps,
  "nativeInputProps" | "multiple"
> & {
  value?: File
  onChange?: (value: File | undefined) => void
}

export const FileInput = ({ onChange, ...props }: FileInputProps) => {
  return (
    <BaseFileInput
      onChange={(e) => (onChange ? onChange(e?.target.files?.[0]) : undefined)}
      multiple={false}
      {...props}
    />
  )
}
