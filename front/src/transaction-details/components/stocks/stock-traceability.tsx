import { useTranslation } from "react-i18next"
import { ExternalLink } from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { formatNumber } from "common/utils/formatters"
import { StockDetails } from "../../types"

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
  parentTransfoRoot = "../stocks/history/",
  childLotRoot = "../../out/history/",
  childTransfoRoot = "../../stocks/history/",
}: TraceabilityProps) => {
  const { t } = useTranslation()

  const parentLot = details?.parent_lot ?? undefined
  const parentTransform = details?.parent_transformation ?? undefined

  const childrenLot = details?.children_lot ?? []
  const childrenTransform = details?.children_transformation ?? []

  const hasParent = parentLot !== undefined || parentTransform !== undefined
  const hasChildren = childrenLot.length > 0 || childrenTransform.length > 0

  const childrenLotVolume = childrenLot.reduce(
    (total, child) => total + child.volume,
    0
  )

  const childrenTransformVolume = childrenTransform.reduce(
    (total, child) => total + child.volume_deducted_from_source,
    0
  )

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
                    {formatNumber(parentLot.volume)} L
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
                    {formatNumber(parentTransform.volume_deducted_from_source)}{" "}
                    L
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
                    {formatNumber(child.volume)} L
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
                    {formatNumber(child.volume_destination)} L (
                    {t(child.source_stock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatNumber(child.volume_deducted_from_source)} L)
                  </b>
                </ExternalLink>
              </li>
            ))}
          </ul>
        </section>
      )}

      <footer>
        {t("Volume total transféré aux enfants:")}{" "}
        <b>{formatNumber(childrenLotVolume + childrenTransformVolume)} L</b>
      </footer>
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
