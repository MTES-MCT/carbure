import { Trans, useTranslation } from "react-i18next"
import { Title } from "common/components"
import { LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit } from "common-v2/components/icons"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import { useUserContext } from "carbure/hooks/user"

export const AccountAuthentication = () => {
  const { t } = useTranslation()
  const user = useUserContext()

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
        <LabelInput readOnly label={t("Addresse email")} value={user.email} />
      </SectionBody>
    </Section>
  )
}
