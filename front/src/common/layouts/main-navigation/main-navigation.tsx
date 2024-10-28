import { PropsWithChildren, useContext } from "react"
import { MainNavigationContext } from "./main-navigation.context"
import styles from "./main-navigation.module.css"
import { fr } from "@codegouvfr/react-dsfr"
import { Text } from "common/components/text"
import { useUser } from "carbure/hooks/user"
import { PrivateSidebar } from "./private-sidebar"
import { PublicSidebar } from "./public-sidebar"

export const MainNavigation = ({ children }: PropsWithChildren) => {
  const { title } = useContext(MainNavigationContext)
  const user = useUser()

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
        <div className={styles["sidebar"]}>
          {user.isAuthenticated() ? <PrivateSidebar /> : <PublicSidebar />}
        </div>

        <section className={styles["page"]}>{children}</section>
      </div>
    </div>
  )
}
