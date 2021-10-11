import cl from "clsx"
import { Box } from "."
import styles from "./tabs.module.css"

type Tab = { key: string; label: string }

type TabsProps = {
  tabs: (Tab | false)[]
  focus: string
  onFocus: (focus: string) => void
}

export const Tabs = ({ tabs, focus, onFocus, ...props }: TabsProps) => {
  return (
    <Box row {...props}>
      {(tabs.filter(Boolean) as Tab[]).map(({ key, label }) => (
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
