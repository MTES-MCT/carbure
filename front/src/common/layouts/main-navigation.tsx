import { PropsWithChildren, useContext } from "react"
import { MainNavigationContext } from "./main-navigation.context"
import styles from "./main-navigation.module.css"
import { fr } from "@codegouvfr/react-dsfr"
import { Text } from "common/components/text"

export const MainNavigation = ({ children }: PropsWithChildren) => {
  const { title } = useContext(MainNavigationContext)
  const a = Array.from({ length: 100 })

  return (
    <div>
      <header className={styles.header}>
        <div className={styles["header-left"]}>
          <Text is="h2" size="xl">
            Carbure
          </Text>
        </div>
        <div className={styles["header-right"]}>
          <Text is="h1">{title}</Text>
        </div>
      </header>
      <div className={styles["body"]}>
        <div className={styles["nav-wrapper"]}>
          <nav className={styles["nav"]}>
            {a.map((_, index) => (
              <div key={index}>element {index}</div>
            ))}
          </nav>
          <div className={styles["bottom-nav"]}>BOTTOM NAV</div>
        </div>

        <section className={styles["page"]}>{children}</section>
      </div>
    </div>
  )
}
