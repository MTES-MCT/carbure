import { Trans } from "react-i18next"
import { Main } from "common-v2/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import Exit from "carbure/components/exit"
import { useUser } from "carbure/hooks/user"

const Account = () => {
  const user = useUser()

  if (!user.isAuthenticated()) {
    return <Exit to="/accounts/login" />
  }

  return (
    <Main>
      <header>
        <h1>
          <Trans>Mon compte</Trans>
        </h1>
      </header>

      <section>
        <AccountAccesRights />
      </section>

      <section>
        <AccountAuthentication />
      </section>
    </Main>
  )
}

export default Account
