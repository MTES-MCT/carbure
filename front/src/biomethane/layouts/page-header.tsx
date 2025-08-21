import Badge from "@codegouvfr/react-dsfr/Badge"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Title } from "common/components/title"
import { PropsWithChildren } from "react"
import { useTranslation } from "react-i18next"
import { declarationInterval } from "biomethane/utils"

export interface BiomethanePageHeaderProps extends PropsWithChildren {
  selectedYear?: number
  yearsOptions: { label: string; value: number }[]
  status: "pending" | "validated"
}

export const BiomethanePageHeader = ({
  selectedYear,
  yearsOptions,
  children,
  status,
}: BiomethanePageHeaderProps) => {
  const { t } = useTranslation()
  const selectedYearIsInCurrentInterval =
    selectedYear === declarationInterval.year

  return (
    <Main>
      <Row>
        <Select options={yearsOptions} value={selectedYear} />
        <Button
          onClick={() => {}}
          iconId="ri-file-text-line"
          asideX
          disabled={!selectedYearIsInCurrentInterval || status === "validated"}
        >
          {t("Valider mes informations annuelles")}
        </Button>
      </Row>
      <Row
        style={{
          justifyContent: "space-between",
          marginTop: "var(--spacing-2w)",
        }}
      >
        <Title
          is="h1"
          as="h5"
          style={{ color: "var(--artwork-major-blue-france" }}
        >
          {t("Récapitulatif de vos informations")}
        </Title>
        <Badge severity={status === "pending" ? "info" : "success"}>
          {status === "pending" ? t("En cours") : t("Validé")}
        </Badge>
      </Row>
      {selectedYearIsInCurrentInterval && (
        <Notice variant="info" icon="ri-time-line" isClosable>
          {t("A déclarer et mettre à jour une fois par an, avant le {{date}}", {
            date: `31/03/${selectedYear + 1}`,
          })}
        </Notice>
      )}
      <Content marginTop>{children}</Content>
    </Main>
  )
}
