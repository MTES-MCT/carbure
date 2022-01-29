import { Trans, useTranslation } from "react-i18next"
import { Main } from "common-v2/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useTitle from "common-v2/hooks/title"

const Account = () => {
  const { t } = useTranslation()
  useTitle(t("Mon compte"))

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
