import useEntity from "carbure/hooks/entity"
import { useUser } from "carbure/hooks/user"
import { Select } from "common/components/selects2"
import { Text } from "common/components/text"
import styles from "./entity-selector.module.css"
import { EntityType } from "carbure/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useMatomo } from "matomo"
import { useNavigate } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"

export const EntitySelector = ({ className }: { className?: string }) => {
  const user = useUser()
  const entity = useEntity()
  const { t } = useTranslation()
  const matomo = useMatomo()
  const navigate = useNavigate()

  const options = user.rights.map((right) => ({
    ...right,
    label: right.entity.name,
    value: right.entity.id,
  }))

  const shortName = useMemo(() => {
    switch (entity.entity_type) {
      case EntityType.Administration:
        return t("Admin")
      case EntityType.Operator:
        return t("Opérateur")
      case EntityType.Producer:
        return t("Producteur")
      case EntityType.Auditor:
        return t("Auditeur")
      case EntityType.Trader:
        return t("Trader")
      case EntityType.ExternalAdmin:
        return t("Admin Externe")
      case EntityType.Airline:
        return t("Compagnie aérienne")
      case EntityType.CPO:
        return t("Aménageur")
      case EntityType.PowerOrHeatProducer:
        return t("Producteur")
      case EntityType.Unknown:
      default:
        return t("Inconnu")
    }
  }, [entity.entity_type, t])

  return (
    <Select
      options={options}
      value={entity.id}
      valueRenderer={(item) => (
        <div className={styles["entity-selector"]}>
          <Text fontWeight="bold" className={styles["entity-selector-name"]}>
            {item.label}
          </Text>
          <Text size="xs" className={styles["entity-selector-type"]}>
            {shortName}
          </Text>
        </div>
      )}
      full
      className={className}
      onChange={(entityId) => {
        if (entityId) {
          matomo.push([
            "trackEvent",
            "menu",
            "change-entity",
            ROUTE_URLS.ORG(entityId),
          ])
          navigate(ROUTE_URLS.ORG(entityId))
        }
      }}
    />
  )
}
