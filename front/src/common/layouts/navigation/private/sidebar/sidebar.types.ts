import { IconName } from "common/components/icon"

export type MenuSection = {
  title: string
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
