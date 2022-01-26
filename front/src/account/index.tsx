import { Trans } from "react-i18next"
import { Main } from "common-v2/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"

const Account = () => (
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

export default Account
