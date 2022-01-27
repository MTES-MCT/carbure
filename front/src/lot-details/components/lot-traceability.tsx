import { useTranslation } from "react-i18next"
import { ExternalLink } from "common-v2/components/button"
import Collapse from "common-v2/components/collapse"
import { formatNumber } from "common-v2/utils/formatters"
import { LotDetails } from "lot-details/types"
import { Split } from "common-v2/components/icons"

export interface TraceabilityProps {
  details: LotDetails | undefined
}

export const LotTraceability = ({ details }: TraceabilityProps) => {
  const { t } = useTranslation()

  const parentLot = details?.parent_lot ?? undefined
  const parentStock = details?.parent_stock ?? undefined

  const childrenLot = details?.children_lot ?? []
  const childrenStock = details?.children_stock ?? []

  const hasParent = parentLot !== undefined || parentStock !== undefined
  const hasChildren = childrenLot.length > 0 || childrenStock.length > 0

  const childrenLotVolume = childrenLot.reduce(
    (total, child) => total + child.volume,
    0
  )

  const childrenTransformVolume = childrenStock.reduce(
    (total, child) => total + child.initial_volume,
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
                <ExternalLink to={`../../in/${parentLot.id}`}>
                  Lot {parentLot.carbure_id}:
                  <b>
                    {t(parentLot.biofuel?.code ?? "", { ns: "biofuels" })}{" "}
                    {formatNumber(parentLot.volume)} L
                  </b>
                </ExternalLink>
              </li>
            )}

            {parentStock && (
              <li>
                <ExternalLink to={`../stocks/${parentStock.id}`}>
                  Stock {parentStock.carbure_id}:
                  <b>
                    {t(parentStock.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatNumber(parentStock.initial_volume)} L
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
                <ExternalLink to={`../../out/${child.id}`}>
                  Lot {child.carbure_id}:{" "}
                  <b>
                    {t(child.biofuel?.code ?? "", { ns: "biofuels" })}{" "}
                    {formatNumber(child.volume)} L
                  </b>
                </ExternalLink>
              </li>
            ))}

            {childrenStock?.map((child, i) => (
              <li key={i}>
                <ExternalLink to={`../../stocks/${child.id}`}>
                  Stock {child.carbure_id}:{" "}
                  <b>
                    {t(child.biofuel?.code ?? "", {
                      ns: "biofuels",
                    })}{" "}
                    {formatNumber(child.initial_volume)} L
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
