import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { AnnualDeclarationStatus } from "biomethane/types"
import { usePageHeaderActions } from "./page-header.hooks"
import useEntity from "common/hooks/entity"
import { PropsWithChildren } from "react"
import { AnnualDeclarationStatusBadge } from "biomethane/components/annual-declaration-status-badge"
import { useAnnualDeclarationYears } from "biomethane/hooks/use-annual-declaration-years"

// Digestate / Energy / Supply Plan pages share the same page header and the same declaration validation logic
export const BiomethanePageHeader = ({ children }: PropsWithChildren) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const years = useAnnualDeclarationYears()

  const {
    selectedYear,
    currentAnnualDeclaration,
    isInDeclarationPeriod,
    hasAnnualDeclarationMissingObjects,
  } = useAnnualDeclaration()

  const {
    openValidateDeclarationDialog,
    openMissingFieldsDialog,
    correctAnnualDeclarationMutation,
  } = usePageHeaderActions()

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
        {isInDeclarationPeriod && (
          <AnnualDeclarationStatusBadge status={status} />
        )}
      </Row>
      {currentAnnualDeclaration?.is_open && entity.canWrite() && (
        <Notice
          variant={
            status === AnnualDeclarationStatus.OVERDUE ? "warning" : "info"
          }
          icon="ri-time-line"
        >
          {status === AnnualDeclarationStatus.OVERDUE
            ? t(
                "Vous avez dépassé les délais de déclaration pour {{year}}, l'administration se réserve le droit de la refuser.",
                {
                  year: selectedYear,
                }
              )
            : t(
                "A déclarer et mettre à jour une fois par an, avant le {{date}}",
                {
                  date: `31/03/${selectedYear + 1}`,
                }
              )}
          {(status === AnnualDeclarationStatus.IN_PROGRESS ||
            status === AnnualDeclarationStatus.OVERDUE) && (
            <Button
              onClick={
                currentAnnualDeclaration?.is_complete
                  ? openValidateDeclarationDialog
                  : openMissingFieldsDialog
              }
              iconId="ri-file-text-line"
              asideX
              disabled={hasAnnualDeclarationMissingObjects}
            >
              {t("Transmettre mes informations annuelles")}
            </Button>
          )}
          {status === AnnualDeclarationStatus.DECLARED && (
            <Button
              onClick={() => correctAnnualDeclarationMutation.execute()}
              iconId="ri-edit-line"
              asideX
              loading={correctAnnualDeclarationMutation.loading}
            >
              {t("Corriger mes informations annuelles")}
            </Button>
          )}
        </Notice>
      )}
      <Content marginTop>{children}</Content>
    </Main>
  )
}
