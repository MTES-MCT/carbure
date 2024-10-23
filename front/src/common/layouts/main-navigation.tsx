import { PropsWithChildren, useContext } from "react"
import { MainNavigationContext } from "./main-navigation.context"
import styles from "./main-navigation.module.css"

export const MainNavigation = ({ children }: PropsWithChildren) => {
  const { title } = useContext(MainNavigationContext)

  return (
    <div>
      <header className={styles.header}>
        <div className={styles["header-left"]}>CarbuRe</div>
        <div className={styles["header-right"]}>{title}</div>
      </header>
      <div className={styles["body"]}>
        <nav className={styles["nav"]}>NAV</nav>
        <section className={styles["page"]}>{children}</section>
      </div>
    </div>
  )
}
