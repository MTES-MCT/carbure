import React from "react"
import cl from "clsx"

// icons were adapted from https://github.com/tabler/tabler-icons

type IconProps = {
  size?: number
  color?: string
  stroke?: number
  className?: string
  [k: string]: string | number | void
}

export const ChevronDown = ({
  size = 24,
  color = "currentColor",
  stroke = 2,
  className,
  ...props
}: IconProps) => (
  <svg
    className={cl("icon", "icon-chevron-down", className)}
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
    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
    <polyline points="6 9 12 15 18 9" />
  </svg>
)

export const Plus = ({
  size = 24,
  color = "currentColor",
  stroke = 2,
  className,
  ...props
}: IconProps) => (
  <svg
    className={cl("icon", "icon-plus", className)}
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
    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
    <line x1={12} y1={5} x2={12} y2={19} />
    <line x1={5} y1={12} x2={19} y2={12} />
  </svg>
)
