import { Trans, useTranslation } from "react-i18next"
import { Main } from "common/components/scaffold"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useTitle from "common/hooks/title"

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
