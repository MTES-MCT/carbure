import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Box, Col, LoaderOverlay, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { ObjectiveSection } from "./components/objective-section"
import { useQuery } from "common/hooks/async"
import { getObjectives } from "./api"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { DeclareTeneurDialog } from "./components/declare-teneur-dialog"
import { OverallProgress } from "./components/overall-progress"
import { SectorProgress } from "./components/sector-progress/sector-progress"
import { CappedCategoriesProgress } from "./components/capped-categories-progress"
import { ObjectivizedCategoriesProgress } from "./components/objectivized-categories-progress"
import { UnconstrainedCategoriesProgress } from "./components/unconstrained-categories-progress"
import {
  CategoryObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "./types"
import { ValidatePendingTeneurDialog } from "./components/validate-pending-teneur-dialog/validate-pending-teneur-dialog"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ElecOperationSector } from "accounting/types"

const Teneur = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const portal = usePortal()
  usePrivateNavigation(t("Objectifs annuels"))

  const { result, loading } = useQuery(getObjectives, {
    key: "teneur-objectives",
    params: [entity.id, 2025],
  })

  if (loading) {
    return <LoaderOverlay />
  }

  const onCategoryClick = (
    objective: CategoryObjective | UnconstrainedCategoryObjective,
    targetType?: TargetType
  ) => {
    if (objective.code !== ElecOperationSector.ELEC) {
      portal((close) => (
        <DeclareTeneurDialog
          onClose={close}
          objective={objective}
          targetType={targetType}
          sectorObjectives={result?.sectors ?? []}
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
      <Box gap="lg">
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
        {/* Avancement global */}
        <OverallProgress objective={result?.global} />
        <SectorProgress sectors={result?.sectors} />
        <ObjectiveSection
          title={t("Avancement par catégorie de carburants alternatifs")}
        >
          <CappedCategoriesProgress
            categories={result?.capped_categories}
            onCategoryClick={onCategoryClick}
          />
          <ObjectivizedCategoriesProgress
            categories={result?.objectivized_categories}
            onCategoryClick={onCategoryClick}
          />
          <UnconstrainedCategoriesProgress
            categories={result?.unconstrained_categories}
            onCategoryClick={onCategoryClick}
          />
        </ObjectiveSection>
      </Box>
    </>
  )
}

export default Teneur
