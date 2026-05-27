import { useTranslation } from "react-i18next"

import useEntity from "common/hooks/entity"
import { Unit, UserRole } from "common/types"
import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
import { LoaderOverlay } from "common/components/scaffold"
import * as api from "../api/company"
import { EditableCard } from "common/molecules/editable-card"
import { Autocomplete } from "common/components/autocomplete2"
import { Checkbox } from "common/components/inputs2"

const CompanyOptions = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const canModify = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

  const toggleMAC = useMutation({
    mutationFn: (toggle: boolean) => api.toggleMAC(entity.id, toggle),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })

  const toggleTrading = useMutation({
    mutationFn: (toggle: boolean) => api.toggleTrading(entity.id, toggle),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })
  const toggleElec = useMutation({
    mutationFn: (toggle: boolean) => api.toggleElec(entity.id, toggle),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })

  const toggleStocks = useMutation({
    mutationFn: (toggle: boolean) => api.toggleStocks(entity.id, toggle),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })

  const toggleDirectDeliveries = useMutation({
    mutationFn: (toggle: boolean) =>
      api.toggleDirectDeliveries(entity.id, toggle),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })

  const setPreferredUnit = useMutation({
    mutationFn: ({ entityId, unit }: { entityId: number; unit: Unit }) =>
      api.setEntityPreferredUnit(entityId, unit),
    invalidates: [COMMON_QUERY_KEYS.userSettings],
  })

  const isLoading =
    toggleMAC.isPending ||
    toggleStocks.isPending ||
    toggleDirectDeliveries.isPending ||
    toggleTrading.isPending

  return (
    <EditableCard
      title={t("Paramètres de configuration")}
      description={t(
        "Les options ci-dessous vous permettent de personnaliser l'interface de CarbuRe pour n'y montrer que les fonctionnalités pertinentes pour votre activité."
      )}
      headerActions={null}
    >
      {entity.isBiomethaneProducer && (
        <Checkbox
          disabled
          label={t("Ma production de biométhane est soumise aux exigences RED")}
          value={entity.is_red_ii}
        />
      )}
      {entity.isIndustry && (
        <>
          <Autocomplete
            label={t(
              "Ma société préfère afficher les quantités et les opérations en :"
            )}
            value={entity.preferred_unit}
            onChange={(unit) =>
              setPreferredUnit.mutate({ entityId: entity.id, unit: unit! })
            }
            options={[
              {
                value: "l",
                label: t("litres (Éthanol à 20°, autres à 15°)"),
              },
              { value: "kg", label: t("kilogrammes") },
              { value: "MJ", label: t("mégajoules") },
            ]}
          />

          <Checkbox
            disabled={!canModify}
            label={t("Ma société gère un stock sur CarbuRe")}
            value={entity.has_stocks ?? false}
            onChange={toggleStocks.mutate}
          />
          <Checkbox
            disabled={!canModify}
            label={t("Ma société a une activité de négoce")}
            value={entity.has_trading}
            onChange={toggleTrading.mutate}
          />
          <Checkbox
            disabled={!canModify}
            label={t("Ma société effectue des mises à consommation (B100 et ED95 uniquement)")} // prettier-ignore
            value={entity.has_mac ?? false}
            onChange={toggleMAC.mutate}
          />
          <Checkbox
            disabled={!canModify}
            label={t("Ma société effectue des livraisons directes")}
            value={entity.has_direct_deliveries}
            onChange={toggleDirectDeliveries.mutate}
          />
        </>
      )}

      {entity.isOperator && (
        <Checkbox
          disabled={!canModify}
          label={t("Ma société accepte des volumes d'electricité")}
          value={entity.has_elec}
          onChange={toggleElec.mutate}
        />
      )}

      {isLoading && <LoaderOverlay />}
    </EditableCard>
  )
}

export default CompanyOptions
