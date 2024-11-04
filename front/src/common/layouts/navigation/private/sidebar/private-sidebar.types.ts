export type MenuSection = {
  title: string
  condition?: boolean
  children: MenuItem[]
}

export type MenuItem = Omit<MenuSection, "children"> & {
  icon?: React.ElementType
  iconActive?: React.ElementType
  path: string
  additionalInfo?: string | number
  target?: string
}
