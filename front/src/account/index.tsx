import { Trans } from "react-i18next"
import { SettingsGetter } from "settings/hooks/use-get-settings"
import { Main, Title } from "common/components"
import { SettingsHeader, SettingsBody } from "settings/components/common"
import { prompt } from "common/components/dialog"
import {
  AccountAccesRights,
  EntityPrompt,
  AccessRequest,
} from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useAPI from "common/hooks/use-api"
import * as api from "./api"
import Exit from "carbure/components/exit"
import { AppHook } from "carbure/hooks/use-app"

export interface AccountHook {
  isLoading: boolean
  askEntityAccess: () => void
}

function useAccount(settings: SettingsGetter): AccountHook {
  const [requestAccess, resolveAccess] = useAPI(api.requestAccess)

  const isLoading = settings.loading || requestAccess.loading

  async function askEntityAccess() {
    const res = await prompt<AccessRequest>((resolve) => (
      <EntityPrompt onResolve={resolve} />
    ))

    if (res) {
      const { entity, role } = res
      await resolveAccess(entity.id, "", role)
      settings.resolve()
    }
  }

  return {
    isLoading,
    askEntityAccess,
  }
}

type AccountProps = {
  app: AppHook
}

const Account = ({ app }: AccountProps) => {
  const account = useAccount(app.settings)

  if (!app.isAuthenticated()) {
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
        <AccountAccesRights settings={app.settings} account={account} />
        <AccountAuthentication settings={app.settings} />
      </SettingsBody>
    </Main>
  )
}

export default Account
