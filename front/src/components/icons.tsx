import React from "react"
import cl from "clsx"

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
    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
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
