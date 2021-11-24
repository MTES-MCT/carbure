import { Trans } from "react-i18next"
import { Main, Title } from "common/components"
import { SettingsHeader, SettingsBody } from "settings/components/common"
import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import Exit from "carbure/components/exit"
import { useUserContext } from "carbure/hooks/user"

const Account = () => {
  const user = useUserContext()

  if (!user.isAuthenticated()) {
    return <Exit to="/accounts/login" />
  }

  return (
    <Main>
      <SettingsHeader>
        <Title>
          <Trans>Mon compte</Trans>
        </Title>
      </SettingsHeader>

      <SettingsBody>
        <AccountAccesRights />
        <AccountAuthentication />
      </SettingsBody>
    </Main>
  )
}

export default Account
