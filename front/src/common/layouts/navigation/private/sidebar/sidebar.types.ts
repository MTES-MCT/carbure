import { IconName } from "common/components/icon"
import { ReactNode } from "react"

export type MenuSection = {
  title: string

  // Display a badge in the title
  badge?: ReactNode

  condition?: boolean
  children: MenuItem[]
}

export type MenuItem = Omit<MenuSection, "children"> & {
  icon?: IconName
  iconActive?: IconName
  path: string
  additionalInfo?: string | number
  target?: string
}
