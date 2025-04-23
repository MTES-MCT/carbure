import { BaseFileInput, BaseFileInputProps } from "../base-file-input"

export type FileInputProps = Omit<
  BaseFileInputProps,
  "nativeInputProps" | "multiple" | "onChange" | "value"
> & {
  value?: File
  onChange?: (value: File | undefined) => void
}

export const FileInput = ({ onChange, value, ...props }: FileInputProps) => {
  return (
    <BaseFileInput
      {...props}
      value={value}
      onChange={(e) => (onChange ? onChange(e?.target.files?.[0]) : undefined)}
      multiple={false}
      placeholder={value?.name ?? props.placeholder}
    />
  )
}
