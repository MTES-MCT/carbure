import Badge from "@codegouvfr/react-dsfr/Badge"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Title } from "common/components/title"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"

export const Digestate = () => {
  const { t } = useTranslation()
  const { year } = useParams<{ year: string }>()

  return (
    <Main>
      <Row>
        <Select
          options={[{ label: `${t("Année")} 2025`, value: 2025 }]}
          value={2025}
          disabled
        />
        <Button onClick={() => {}} iconId="ri-file-text-line" asideX>
          {t("Valider mes informations annuelles")}
        </Button>
      </Row>
      <Row
        style={{
          justifyContent: "space-between",
          marginTop: "var(--spacing-2w)",
        }}
      >
        <Title is="h1" as="h5">
          {t("Récapitulatif de vos informations")}
        </Title>
        <Badge severity="info">{t("En cours")}</Badge>
      </Row>
      {year && (
        <Notice variant="info" icon="ri-time-line" isClosable>
          {t("A déclarer et mettre à jour une fois par an, avant le {{date}}", {
            date: `31/03/${parseInt(year) + 1}`,
          })}
        </Notice>
      )}
      <Content marginTop>contenu test</Content>
    </Main>
  )
}
