import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Col, LoaderOverlay, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import { getObjectives } from "./api"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { DeclareTeneurDialog } from "./components/declare-teneur-dialog"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ElecOperationSector } from "accounting/types"
import { DeclareElecTeneurDialog } from "./components/declare-elec-teneur-dialog"
import { BetaPage } from "common/molecules/beta-page"
import {
  CategoryObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "./types"
import { ValidatePendingTeneurDialog } from "./components/validate-pending-teneur-dialog/validate-pending-teneur-dialog"
import { ObjectivesContent } from "./components/objectives-content"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"

const Teneur = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const portal = usePortal()
  const { selectedYear, isDeclarationInCurrentPeriod } =
    useAnnualDeclarationTiruert()
  usePrivateNavigation(<BetaPage title={t("Objectifs annuels")} />, "teneur")

  const { result: objectivesData, loading } = useQuery(getObjectives, {
    key: "teneur-objectives",
    params: [entity.id, selectedYear],
  })

  if (loading) {
    return <LoaderOverlay />
  }

  const onCategoryClick = (
    objective: CategoryObjective | UnconstrainedCategoryObjective,
    targetType?: TargetType
  ) => {
    if (objective.code === ElecOperationSector.ELEC) {
      portal((close) => (
        <DeclareElecTeneurDialog
          onClose={close}
          objective={objective}
          mainObjective={objectivesData?.global}
        />
      ))
    } else {
      portal((close) => (
        <DeclareTeneurDialog
          onClose={close}
          objective={objective}
          targetType={targetType}
          sectorObjectives={objectivesData?.sectors ?? []}
          mainObjective={objectivesData?.global}
        />
      ))
    }
  }

  const onValidatePendingTeneurClick = () => {
    portal((close) => <ValidatePendingTeneurDialog onClose={close} />)
  }

  return (
    <>
      <Notice noColor variant="info">
        {t(
          "Bienvenue dans votre espace de teneur et objectifs annuels. Vous pouvez simuler des conversions quantités et tCO2 eq. évitées, ainsi qu'y rentrer vos quantités de teneur mensuelle afin de clôturer votre comptabilité mensuelle."
        )}
      </Notice>
      {isDeclarationInCurrentPeriod && (
        <Notice noColor variant="info">
          <Row style={{ alignItems: "center", width: "100%" }}>
            <Col spread>
              <p>
                <Trans
                  t={t}
                  components={{ strong: <strong /> }}
                  defaults="Toutes vos déclarations enregistrées ne sont pas validées, <strong>pensez à valider votre teneur mensuelle</strong> pour que vos déclarations soient prises en comptes."
                />
              </p>
            </Col>
            <Button priority="primary" onClick={onValidatePendingTeneurClick}>
              {t("Valider ma teneur mensuelle")}
            </Button>
          </Row>
        </Notice>
      )}

      <ObjectivesContent
        objectivesData={objectivesData}
        readOnly={!isDeclarationInCurrentPeriod}
        onCategoryClick={onCategoryClick}
      />
    </>
  )
}

export default Teneur
