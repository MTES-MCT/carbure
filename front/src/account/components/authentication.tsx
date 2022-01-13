import { Trans, useTranslation } from "react-i18next"
import { useUser } from "carbure/hooks/user"
import { TextInput } from "common-v2/components/input"
import { Button } from "common-v2/components/button"
import { Edit } from "common-v2/components/icons"
import { Panel } from "common-v2/components/scaffold"

export const AccountAuthentication = () => {
  const { t } = useTranslation()
  const user = useUser()

  return (
    <Panel>
      <header>
        <h1>
          <Trans>Identifiants</Trans>
        </h1>
        <Button
          asideX
          disabled
          variant="primary"
          icon={Edit}
          label={t("Modifier mes identifiants")}
        />
      </header>

      <footer>
        <TextInput readOnly label={t("Addresse email")} value={user.email} />
      </footer>
    </Panel>
  )
}
