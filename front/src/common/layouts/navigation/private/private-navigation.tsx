import { PropsWithChildren, useContext } from "react"
import cl from "clsx"
import {
  PrivateNavigationContext,
  PrivateNavigationProvider,
} from "./private-navigation.context"
import styles from "./private-navigation.module.css"
import { Text } from "common/components/text"
import { PrivateSidebar } from "./sidebar"

export const PrivateNavigation = ({ children }: PropsWithChildren) => {
  const { title } = useContext(PrivateNavigationContext)

  return (
    <PrivateNavigationProvider>
      <>
        <header className={styles.header}>
          <div className={styles["header-left"]}>
            <Text is="h2" size="xl" fontWeight="bold">
              Carbure
            </Text>
          </div>
          <div className={styles["header-right"]}>
            <Text is="h1" fontWeight="bold">
              {title}
            </Text>
          </div>
        </header>
        <div className={cl(styles["body"])}>
          <div className={styles["sidebar"]}>
            <PrivateSidebar />
          </div>

          <section className={styles["page"]}>{children}</section>
        </div>
      </>
    </PrivateNavigationProvider>
  )
}
