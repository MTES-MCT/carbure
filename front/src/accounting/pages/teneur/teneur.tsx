import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { Box, Col, LoaderOverlay, Row } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { ObjectiveSection } from "./components/objective-section"
import { useQuery } from "common/hooks/async"
import { getAdminObjectivesEntity, getObjectives } from "./api"
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
import { DeclareElecTeneurDialog } from "./components/declare-elec-teneur-dialog"
import { useOutletContext } from "react-router-dom"
import { TeneurOutletContext } from "accounting/layouts/teneur-layout"

function getObjectivesForEntityOrAdmin(
  entityId: number,
  year: number,
  isAdmin: boolean,
  selectedEntityId?: number
) {
  if (isAdmin && selectedEntityId)
    return getAdminObjectivesEntity(entityId, year, selectedEntityId)
  else return getObjectives(entityId, year, isAdmin)
}

const Teneur = () => {
  const entity = useEntity()
  const { isAdmin } = entity
  const isAdminOrExternal = isAdmin || entity.isExternal
  const readOnly = isAdminOrExternal
  const { t } = useTranslation()
  const portal = usePortal()
  usePrivateNavigation(t("Objectifs annuels"))

  const { selectedEntityId } = useOutletContext<TeneurOutletContext>()

  const { result, loading } = useQuery(getObjectivesForEntityOrAdmin, {
    key: "teneur-objectives",
    params: [entity.id, 2025, isAdminOrExternal, selectedEntityId],
  })

  const objectivesData = result

  if (loading) {
    return <LoaderOverlay />
  }

  if (isAdminOrExternal && !selectedEntityId && !objectivesData) {
    return (
      <Notice noColor variant="info">
        {t("Veuillez sélectionner un redevable pour voir ses objectifs.")}
      </Notice>
    )
  }

  const onCategoryClick = (
    objective: CategoryObjective | UnconstrainedCategoryObjective,
    targetType?: TargetType
  ) => {
    if (objective.code === ElecOperationSector.ELEC) {
      portal((close) => (
        <DeclareElecTeneurDialog //
          onClose={close}
          objective={objective}
          mainObjective={result?.global}
        />
      ))
    } else {
      portal((close) => (
        <DeclareTeneurDialog
          onClose={close}
          objective={objective}
          targetType={targetType}
          sectorObjectives={result?.sectors ?? []}
          mainObjective={result?.global}
        />
      ))
    }
  }

  const onValidatePendingTeneurClick = () => {
    portal((close) => <ValidatePendingTeneurDialog onClose={close} />)
  }

  return (
    <>
      {isAdminOrExternal && selectedEntityId ? (
        <Notice noColor variant="info">
          {t("Vous consultez les objectifs du redevable sélectionné.")}
        </Notice>
      ) : isAdminOrExternal ? (
        <Notice noColor variant="info">
          {t("Sur cette page, vous avez accès aux objectifs consolidés.")}
          <br />
          {t(
            "Vous pouvez également sélectionner un redevable pour consulter ses objectifs."
          )}
        </Notice>
      ) : (
        <Notice noColor variant="info">
          {t(
            "Bienvenue dans votre espace de teneur et objectifs annuels. Vous pouvez simuler des conversions quantités et tCO2 eq. évitées, ainsi qu'y rentrer vos quantités de teneur mensuelle afin de clôturer votre comptabilité mensuelle."
          )}
        </Notice>
      )}
      <Box gap="lg">
        {!isAdminOrExternal && (
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
        {/* Avancement global */}
        <OverallProgress objective={objectivesData?.global} />
        <SectorProgress sectors={objectivesData?.sectors} />
        <ObjectiveSection
          title={t("Avancement par catégorie de carburants alternatifs")}
        >
          <CappedCategoriesProgress
            categories={objectivesData?.capped_categories}
            onCategoryClick={onCategoryClick}
            readOnly={readOnly}
          />
          <ObjectivizedCategoriesProgress
            categories={objectivesData?.objectivized_categories}
            onCategoryClick={onCategoryClick}
            readOnly={readOnly}
          />
          <UnconstrainedCategoriesProgress
            categories={objectivesData?.unconstrained_categories}
            onCategoryClick={onCategoryClick}
            readOnly={readOnly}
          />
        </ObjectiveSection>
      </Box>
    </>
  )
}

export default Teneur
