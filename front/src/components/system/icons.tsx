import React from "react"
import cl from "clsx"

import styles from "./icons.module.css"

// icons were adapted from https://github.com/tabler/tabler-icons

type IconProps = {
  size?: number
  color?: string
  stroke?: number
  className?: string
  title?: string
  [k: string]: any
}

const Icon = ({
  size = 24,
  color = "currentColor",
  stroke = 2,
  className,
  title,
  children,
  ...props
}: IconProps) => (
  <svg
    className={cl("icon", className)}
    width={size}
    height={size}
    viewBox="0 0 24 24"
    strokeWidth={stroke}
    stroke={color}
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <title>{title}</title>
    {children}
  </svg>
)

export const ChevronDown = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-chevron-down", className)}>
    <polyline points="6 9 12 15 18 9" />
  </Icon>
)

export const ChevronLeft = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-chevron-down", className)}>
    <polyline points="15 6 9 12 15 18" />
  </Icon>
)

export const ChevronRight = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-chevron-right", className)}>
    <polyline points="9 6 15 12 9 18" />
  </Icon>
)

export const Plus = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-plus", className)}>
    <line x1={12} y1={5} x2={12} y2={19} />
    <line x1={5} y1={12} x2={19} y2={12} />
  </Icon>
)

export const Search = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-search", className)}>
    <circle cx="10" cy="10" r="7" />
    <line x1="21" y1="21" x2="15" y2="15" />
  </Icon>
)

export const Cross = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-cross", className)}>
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </Icon>
)

export const AlertCircle = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-cross", className)}>
    <circle cx="12" cy="12" r="9" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </Icon>
)

export const Copy = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-cross", className)}>
    <rect x="8" y="8" width="12" height="12" rx="2" />
    <path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2" />
  </Icon>
)

export const Check = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-cross", className)}>
    <path d="M5 12l5 5l10 -10" />
  </Icon>
)

export const Save = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-save", className)}>
    <path d="M6 4h10l4 4v10a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2" />
    <circle cx="12" cy="14" r="2" />
    <polyline points="14 4 14 8 8 8 8 4" />
  </Icon>
)

export const Message = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-message", className)}>
    <path d="M4 21v-13a3 3 0 0 1 3 -3h10a3 3 0 0 1 3 3v6a3 3 0 0 1 -3 3h-9l-4 4" />
    <line x1="12" y1="8" x2="12" y2="11" />
    <line x1="12" y1="14" x2="12" y2="14.01" />
  </Icon>
)

export const Loader = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-loader", styles.loader, className)}>
    <line x1="12" y1="6" x2="12" y2="3" />
    <line x1="16.25" y1="7.75" x2="18.4" y2="5.6" />
    <line x1="18" y1="12" x2="21" y2="12" />
    <line x1="16.25" y1="16.25" x2="18.4" y2="18.4" />
    <line x1="12" y1="18" x2="12" y2="21" />
    <line x1="7.75" y1="16.25" x2="5.6" y2="18.4" />
    <line x1="6" y1="12" x2="3" y2="12" />
    <line x1="7.75" y1="7.75" x2="5.6" y2="5.6" />
  </Icon>
)

export const Rapport = ({ className, ...props }: IconProps) => (
  <Icon {...props} className={cl("icon-rapport", className)}>
      <path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" />
      <rect x="9" y="3" width="6" height="4" rx="2" />
      <line x1="9" y1="12" x2="9.01" y2="12" />
      <line x1="13" y1="12" x2="15" y2="12" />
      <line x1="9" y1="16" x2="9.01" y2="16" />
      <line x1="13" y1="16" x2="15" y2="16" />
  </Icon> 
)
