import cl from "clsx"
import { Box } from "."
import styles from "./tabs.module.css"

type TabsProps = {
  tabs: { key: string; label: string }[]
  focus: string
  onFocus: (focus: string) => void
}

export const Tabs = ({ tabs, focus, onFocus, ...props }: TabsProps) => {
  return (
    <Box row {...props}>
      {tabs.map(({ key, label }) => (
        <span
          key={key}
          onClick={() => onFocus(key)}
          className={cl(styles.tabHeader, key === focus && styles.tabFocus)}
        >
          {label}
        </span>
      ))}
    </Box>
  )
}

export default Tabs
