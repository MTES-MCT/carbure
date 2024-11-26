import { useUser } from "carbure/hooks/user"
import cl from "clsx"
import { PropsWithChildren } from "react"
import { PrivateNavigation } from "./private/private-navigation"
import { PublicNavigation } from "./public/public-navigation"
import { CarbureFooter } from "./footer"
import { PrivateNavigationProvider } from "./private/private-navigation.context"
import { DevBanner } from "common/components/dev-banner"
import css from "./navigation-layout.module.css"

export const NavigationLayout = ({ children }: PropsWithChildren) => {
  const user = useUser()
  return (
    <div
      className={cl(
        css["navigation-layout"],
        user.isAuthenticated() && css["authenticated"]
      )}
    >
      <DevBanner />

      {user.isAuthenticated() ? (
        <PrivateNavigationProvider>
          <PrivateNavigation>{children}</PrivateNavigation>
        </PrivateNavigationProvider>
      ) : (
        <>
          <PublicNavigation />
          {children}
          <CarbureFooter />
        </>
      )}
    </div>
  )
}
