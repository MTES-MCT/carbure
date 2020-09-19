import React, { CSSProperties } from "react"
import cl from "clsx"

import styles from "./system.module.css"
import { ChevronDown } from "./icons"

type SelectProps = {
  className?: string
  style?: CSSProperties
  children: React.ReactNode
  [k: string]: any // ...props
}

export const Select = ({
  style,
  className,
  children,
  ...props
}: SelectProps) => (
  <div style={style} className={cl(styles.selectWrapper, className)}>
    <select {...props} className={styles.select}>
      {children}
    </select>
    <ChevronDown className={styles.selectArrow} />
  </div>
)

