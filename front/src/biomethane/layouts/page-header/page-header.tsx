import Badge from "@codegouvfr/react-dsfr/Badge"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import useYears from "common/hooks/years-2"
import { getAnnualDeclarationYears } from "biomethane/api"
import { Outlet } from "react-router-dom"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"
import { AnnualDeclarationStatus } from "biomethane/types"
import { usePageHeaderActions } from "./page-header.hooks"

// Digestate and Energy pages share the same page header and the same declaration validation logic
export const BiomethanePageHeader = () => {
  const { t } = useTranslation()
  const years = useYears("biomethane", getAnnualDeclarationYears)
  const { selectedYear, currentAnnualDeclaration, isInDeclarationPeriod } =
    useAnnualDeclaration()
  const { openValidateDeclarationDialog, openCorrectionDeclarationDialog } =
    usePageHeaderActions()

  const status =
    currentAnnualDeclaration?.status ?? AnnualDeclarationStatus.IN_PROGRESS

  return (
    <Main>
      <Row style={{ justifyContent: "space-between", alignItems: "center" }}>
        <Select
          options={years.options}
          value={selectedYear}
          onChange={years.setYear}
        />
        <Badge
          severity={
            status === AnnualDeclarationStatus.DECLARED ? "success" : "info"
          }
        >
          {status === AnnualDeclarationStatus.DECLARED
            ? t("Déclaration transmise")
            : t("Déclaration en cours")}
        </Badge>
      </Row>
      {isInDeclarationPeriod && (
        <Notice variant="info" icon="ri-time-line">
          {t("A déclarer et mettre à jour une fois par an, avant le {{date}}", {
            date: `31/03/${selectedYear + 1}`,
          })}
          {status === AnnualDeclarationStatus.IN_PROGRESS && (
            <Button
              onClick={openValidateDeclarationDialog}
              iconId="ri-file-text-line"
              asideX
            >
              {t("Transmettre mes informations annuelles")}
            </Button>
          )}
          {status === AnnualDeclarationStatus.DECLARED && (
            <Button
              onClick={openCorrectionDeclarationDialog}
              iconId="ri-edit-line"
              asideX
            >
              {t("Corriger mes informations annuelles")}
            </Button>
          )}
        </Notice>
      )}
      <Content marginTop>
        <Outlet />
      </Content>
    </Main>
  )
}
