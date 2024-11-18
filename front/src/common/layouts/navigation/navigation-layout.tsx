import { useUser } from "carbure/hooks/user"
import { PropsWithChildren } from "react"
import { PrivateNavigation } from "./private/private-navigation"
import { PublicNavigation } from "./public/public-navigation"
import { CarbureFooter } from "./footer"
// import { DevBanner } from "common/components/dev-banner"

export const NavigationLayout = ({ children }: PropsWithChildren) => {
  const user = useUser()
  return (
    <>
      {/* Find a way to calculate the body height with dev banner */}
      {/* <DevBanner /> */}

      {user.isAuthenticated() ? (
        <PrivateNavigation>{children}</PrivateNavigation>
      ) : (
        <>
          <PublicNavigation />
          {children}
          <CarbureFooter />
        </>
      )}
    </>
  )
}
