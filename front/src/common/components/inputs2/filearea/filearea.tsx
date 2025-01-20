import { Col, Overlay } from "common/components/scaffold"
import { useState } from "react"
import styles from "./filearea.module.css"
import { IconProps } from "common/components/icon"

export interface FileAreaProps {
  className?: string
  style?: React.CSSProperties
  children?: React.ReactNode
  label?: string
  icon: React.ComponentType<IconProps>
  value?: File | undefined
  onChange?: (value: File | undefined) => void
}

export const FileArea = ({
  children,
  icon: Icon,
  label,
  onChange,
  ...props
}: FileAreaProps) => {
  const [active, setActive] = useState(false)

  return (
    <div
      {...props}
      data-active={active ? true : undefined}
      onDragOver={(e) => {
        e.preventDefault()
        if (!active && e.dataTransfer.types.includes("Files")) {
          setActive(true)
        }
      }}
      onDragLeave={(e) => {
        e.preventDefault()
        if (!e.currentTarget.contains(e.relatedTarget as Element)) {
          setActive(false)
        }
      }}
      onDrop={(e) => {
        e.preventDefault()
        if (e.dataTransfer.files.length > 0) {
          onChange?.(e.dataTransfer.files[0])
          setActive(false)
        }
      }}
    >
      {children}
      {active && (
        <Overlay>
          <Col className={styles.fileplaceholder}>
            <Icon size="lg" />
            {label}
          </Col>
        </Overlay>
      )}
    </div>
  )
}
