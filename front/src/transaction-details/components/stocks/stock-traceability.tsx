import { useTranslation } from "react-i18next"
import { ExternalLink } from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { formatUnit } from "common/utils/formatters"
import { StockDetails } from "../../types"
import useEntity from "common/hooks/entity"
import { Unit } from "common/types"

export interface TraceabilityProps {
  details: StockDetails | undefined
  parentLotRoot?: string
  parentTransfoRoot?: string
  childLotRoot?: string
  childTransfoRoot?: string
}

export const StockTraceability = ({
  details,
  parentLotRoot = "../in/history",
  parentTransfoRoot = "history",
  childLotRoot = "../out/history",
  childTransfoRoot = "history",
}: TraceabilityProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const parentLot = details?.parent_lot ?? undefined
  const parentTransform = details?.parent_transformation ?? undefined

  const childrenLot = details?.children_lot ?? []
  const childrenTransform = details?.children_transformation ?? []

  const hasParent = parentLot !== undefined || parentTransform !== undefined
  const hasChildren = childrenLot.length > 0 || childrenTransform.length > 0

  const unit = entity.preferred_unit ?? Unit.l

  const unitToLotField = {
    l: "volume" as const,
    kg: "weight" as const,
    MJ: "lhv_amount" as const,
  }

  const unitToStockField = {
    l: "initial_volume" as const,
    kg: "initial_weight" as const,
    MJ: "initial_lhv_amount" as const,
  }

  const lotField = unitToLotField[unit]
  const stockField = unitToStockField[unit]

  return (
    <Collapse icon={Split} variant="info" label={t("Traçabilité")}>
      {hasParent && (
        <section>
          <b>{t("Parent")}</b>
          <ul>
            {parentLot && (
              <li>
                <ExternalLink to={`${parentLotRoot}#lot/${parentLot.id}`}>
                  Lot {parentLot.carbure_id}:
                  <b>
                    {t(parentLot.biofuel?.code ?? "", { ns: "biofuels" })}{" "}
                    {formatUnit(parentLot[lotField], unit)}
                  </b>
                </ExternalLink>
              </li>
            )}

            {parentTransform && (
              <li>
                <ExternalLink
                  to={`${parentTransfoRoot}#stock/${parentTransform.source_stock.id}`}
                >
                  Stock {parentTransform.source_stock.carbure_id}:
                  <b>
                    {t(parentTransform.source_stock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(parentTransform.source_stock[stockField], unit)}{" "}
                    (-
                    {formatUnit(
                      parentTransform.volume_deducted_from_source,
                      Unit.l
                    )}
                    )
                  </b>
                </ExternalLink>
              </li>
            )}
          </ul>
        </section>
      )}

      {hasChildren && (
        <section>
          <b>{t("Enfants")}</b>
          <ul>
            {childrenLot?.map((child) => (
              <li key={child.id}>
                <ExternalLink to={`${childLotRoot}#lot/${child.id}`}>
                  Lot {child.carbure_id}:{" "}
                  <b>
                    {t(child.biofuel?.code ?? "", { ns: "biofuels" })}{" "}
                    {formatUnit(child[lotField], unit)}
                  </b>
                </ExternalLink>
              </li>
            ))}

            {childrenTransform?.map((child, i) => (
              <li key={i}>
                <ExternalLink
                  to={`${childTransfoRoot}#stock/${child.dest_stock.id}`}
                >
                  Stock {child.dest_stock.carbure_id}:{" "}
                  <b>
                    {t(child.dest_stock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(child.dest_stock[stockField], unit)} (-
                    {formatUnit(child.volume_deducted_from_source, Unit.l)})
                  </b>
                </ExternalLink>
              </li>
            ))}
          </ul>
        </section>
      )}

      <footer />
    </Collapse>
  )
}

export function hasTraceability(details: StockDetails | undefined) {
  if (details === undefined) return false

  return (
    details.parent_lot !== null ||
    details.parent_transformation !== null ||
    (details.children_lot && details.children_lot.length > 0) ||
    (details.children_transformation &&
      details.children_transformation.length > 0)
  )
}

export default StockTraceability
