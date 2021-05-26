import { Trans, useTranslation } from "react-i18next"
import { SettingsGetter } from "settings/hooks/use-get-settings"
import { Title } from "common/components"
import { LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit } from "common/components/icons"
import { Section, SectionBody, SectionHeader } from "common/components/section"

type AccountAuthenticationProps = {
  settings: SettingsGetter
}

export const AccountAuthentication = ({
  settings,
}: AccountAuthenticationProps) => {
  const { t } = useTranslation()

  return (
    <Section>
      <SectionHeader>
        <Title>
          <Trans>Identifiants</Trans>
        </Title>
        <Button disabled level="primary" icon={Edit}>
          <Trans>Modifier mes identifiants</Trans>
        </Button>
      </SectionHeader>

      <SectionBody>
        <LabelInput
          readOnly
          label={t("Addresse email")}
          value={settings.data?.email ?? ""}
        />
      </SectionBody>
    </Section>
  )
}
