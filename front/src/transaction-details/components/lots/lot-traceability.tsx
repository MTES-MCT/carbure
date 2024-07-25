import { useTranslation } from "react-i18next"
import { ExternalLink } from "common/components/button"
import Collapse from "common/components/collapse"
import { formatUnit } from "common/utils/formatters"
import { LotDetails } from "transaction-details/types"
import { Split } from "common/components/icons"
import useEntity from "carbure/hooks/entity"

export interface TraceabilityProps {
  details: LotDetails | undefined
  parentLotRoot?: string
  parentStockRoot?: string
  childLotRoot?: string
  childStockRoot?: string
}

export const LotTraceability = ({
  details,
  parentLotRoot = "../in/history",
  parentStockRoot = "../stocks/history",
  childLotRoot = "../out/history",
  childStockRoot = "../stocks/history",
}: TraceabilityProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const parentLot = details?.parent_lot ?? undefined
  const parentStock = details?.parent_stock ?? undefined

  const childrenLot = details?.children_lot ?? []
  const childrenStock = details?.children_stock ?? []

  const hasParent = parentLot !== undefined || parentStock !== undefined
  const hasChildren = childrenLot.length > 0 || childrenStock.length > 0

  const unit = entity.preferred_unit ?? "l"

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

            {parentStock && (
              <li>
                <ExternalLink to={`${parentStockRoot}#stock/${parentStock.id}`}>
                  Stock {parentStock.carbure_id}:
                  <b>
                    {t(parentStock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(parentStock[stockField], unit)}
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

            {childrenStock?.map((child, i) => (
              <li key={i}>
                <ExternalLink to={`${childStockRoot}#stock/${child.id}`}>
                  Stock {child.carbure_id}:{" "}
                  <b>
                    {t(child.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatUnit(child[stockField], unit)}
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

export function hasTraceability(details: LotDetails | undefined) {
  if (details === undefined) return false

  return (
    details.parent_lot !== null ||
    details.parent_stock !== null ||
    (details.children_lot && details.children_lot.length > 0) ||
    (details.children_stock && details.children_stock.length > 0)
  )
}

export default LotTraceability
