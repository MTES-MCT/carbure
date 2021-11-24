import { ExternalLink } from "common-v2/components/button"
import Collapse from "common-v2/components/collapse"
import { formatNumber } from "common-v2/utils/formatters"
import { useTranslation } from "react-i18next"
import { StockDetails } from "stock-details/types"

export interface TraceabilityProps {
  details: StockDetails | undefined
}

export const StockTraceability = ({ details }: TraceabilityProps) => {
  const { t } = useTranslation()

  const parentLot = details?.parent_lot
  const parentTransform = details?.parent_transformation

  const childrenLot = details?.children_lot ?? []
  const childrenTransform = details?.children_transformation ?? []

  const noChildren = childrenLot.length === 0 && childrenTransform.length === 0

  const childrenLotVolume = childrenLot.reduce(
    (total, child) => total + child.volume,
    0
  )

  const childrenTransformVolume = childrenTransform.reduce(
    (total, child) => total + child.volume_destination,
    0
  )

  return (
    <Collapse variant="info" label={t("Traçabilité")}>
      <section>
        <b>{t("Parent")}</b>
        <ul>
          {parentLot && (
            <li>
              <ExternalLink to={`../../in/${parentLot.id}`}>
                Lot {parentLot.carbure_id}:
                <b>{formatNumber(parentLot.volume)} L</b>
              </ExternalLink>
            </li>
          )}

          {parentTransform && (
            <li>
              <ExternalLink to={`../${parentTransform.source_stock}`}>
                Stock {parentTransform.source_stock}:
                <b>{formatNumber(parentTransform.volume_destination)} L</b>
              </ExternalLink>
            </li>
          )}
        </ul>
      </section>

      <section>
        <b>{t("Enfants")}</b>
        <ul>
          {childrenLot?.map((child) => (
            <li key={child.id}>
              <ExternalLink to={`../../out/${child.id}`}>
                Lot {child.carbure_id}: <b>{formatNumber(child.volume)} L</b>
              </ExternalLink>
            </li>
          ))}

          {childrenTransform?.map((child, i) => (
            <li key={i}>
              <ExternalLink to={`../${child.dest_stock}`}>
                Stock {child.dest_stock}:{" "}
                <b>{formatNumber(child.volume_destination)} L</b>
              </ExternalLink>
            </li>
          ))}

          {noChildren && <li>{t("Aucun enfant trouvé")}</li>}
        </ul>
      </section>

      <footer>
        Volume total des enfants:{" "}
        <b>{formatNumber(childrenLotVolume + childrenTransformVolume)} L</b>
      </footer>
    </Collapse>
  )
}

export default StockTraceability
