import cl from "clsx"
import { SystemProps } from "."
import styles from "./sticky.module.css"

const Sticky = ({ className, children }: SystemProps) => {
  return <div className={cl(styles.sticky, className)}>{children}</div>
}

export default Sticky
