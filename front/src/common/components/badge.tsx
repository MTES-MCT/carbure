import { CSSProperties } from 'react'
import cl from "clsx"
import styles from "./badge.module.css"

export type Variant = 'regular' | 'primary' | 'secondary' | 'info' | 'success' | 'warning' | 'danger'

type BadgeProps = {
  big?: boolean
  variant?: Variant
  text?: string
  children?: React.ReactNode
  className?: string,
  style?: CSSProperties
}

const Badge = ({ big, variant, text, className, style, children }: BadgeProps) => {
  return (
    <div
      style={style}
      className={cl(
        styles.badge,
        big && styles.big,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'info' && styles.info,
        variant === 'success' && styles.success,
        variant === 'warning' && styles.warning,
        variant === 'danger' && styles.danger,
        className
      )}
    >
      {text ?? children}
    </div>
  )
}

export default Badge
