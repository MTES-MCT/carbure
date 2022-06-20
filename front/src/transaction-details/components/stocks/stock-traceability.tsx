import { useTranslation } from "react-i18next"
import { ExternalLink } from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { formatUnit } from "common/utils/formatters"
import { StockDetails } from "../../types"
import useEntity from "carbure/hooks/entity"
import Flags from "flags.json"

export interface TraceabilityProps {
  details: StockDetails | undefined
  parentLotRoot?: string
  parentTransfoRoot?: string
  childLotRoot?: string
  childTransfoRoot?: string
}

export const StockTraceability = ({
  details,
  parentLotRoot = "../../in/history/",
  parentTransfoRoot = "../history/",
  childLotRoot = "../../out/history/",
  childTransfoRoot = "../history/",
}: TraceabilityProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const parentLot = details?.parent_lot ?? undefined
  const parentTransform = details?.parent_transformation ?? undefined

  const childrenLot = details?.children_lot ?? []
  const childrenTransform = details?.children_transformation ?? []

  const hasParent = parentLot !== undefined || parentTransform !== undefined
  const hasChildren = childrenLot.length > 0 || childrenTransform.length > 0

  const unit = !Flags.preferred_unit ? "l" : entity.preferred_unit ?? "l"

  const unitToLotField = {
    l: "volume" as "volume",
    kg: "weight" as "weight",
    MJ: "lhv_amount" as "lhv_amount",
  }

  const unitToStockField = {
    l: "initial_volume" as "initial_volume",
    kg: "initial_weight" as "initial_weight",
    MJ: "initial_lhv_amount" as "initial_lhv_amount",
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
                <ExternalLink to={`${parentLotRoot}${parentLot.id}`}>
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
                  to={`${parentTransfoRoot}${parentTransform.source_stock.id}`}
                >
                  Stock {parentTransform.source_stock.carbure_id}:
                  <b>
                    {t(parentTransform.source_stock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(parentTransform.dest_stock[stockField], unit)}
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
                <ExternalLink to={`${childLotRoot}${child.id}`}>
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
                <ExternalLink to={`${childTransfoRoot}${child.dest_stock.id}`}>
                  Stock {child.dest_stock.carbure_id}:{" "}
                  <b>
                    {t(child.dest_stock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(child.dest_stock[stockField], unit)}
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
