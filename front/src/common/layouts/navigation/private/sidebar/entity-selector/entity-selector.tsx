import useEntity from "common/hooks/entity"
import { useUser } from "common/hooks/user"
import { Select } from "common/components/selects2"
import { Text } from "common/components/text"
import styles from "./entity-selector.module.css"
import { EntityType } from "common/types"
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

  const optionsWithAddEntity = [
    {
      label: t("Ajouter une entité"),
      value: "add-entity",
    },
    ...options,
  ]

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
      options={optionsWithAddEntity}
      value={entity.id || ""}
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
        if (entityId === "add-entity") {
          navigate(ROUTE_URLS.MY_ACCOUNT.ADD_COMPANY)
        } else if (entityId) {
          matomo.push([
            "trackEvent",
            "menu",
            "change-entity",
            ROUTE_URLS.ORG(Number(entityId)),
          ])
          navigate(ROUTE_URLS.ORG(Number(entityId)))
        }
      }}
      placeholder={t("Liste des entités")}
    >
      {({ label, value }) => {
        if (value === "add-entity") {
          return <b>{label}</b>
        }
        return label
      }}
    </Select>
  )
}
