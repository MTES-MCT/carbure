import { Country, SiteType, OwnershipType } from "common/types"
import { InfoCircle } from "common/components/icons"
import Tooltip from "common/components/tooltip"
import { ReactNode, useMemo } from "react"
import { useTranslation } from "react-i18next"

export const useDeliverySiteFlags = (depotType?: SiteType) =>
  useMemo(
    () => ({
      isPowerPlant: depotType === SiteType.POWER_PLANT,
      isHeatPlant: depotType === SiteType.HEAT_PLANT,
      isCogenerationPlant: depotType === SiteType.COGENERATION_PLANT,
    }),
    [depotType]
  )

type DepotTypeTranslationItem = {
  type: SiteType
  label: string
  tooltip?: string
}

const useDepotTypeTranslations = () => {
  const { t } = useTranslation()

  return useMemo<DepotTypeTranslationItem[]>(
    () => [
      {
        type: SiteType.EFS,
        label: t("EFS"),
        tooltip: t("Entrepôt fiscal de stockage"),
      },
      {
        type: SiteType.EFPE,
        label: t("EFPE"),
        tooltip: t("Entrepôt fiscal de produits énergétiques"),
      },
      {
        type: SiteType.EFCA,
        label: t("EFCA"),
        tooltip: t("Entrepôt fiscal de carburants d'aviation"),
      },
      {
        type: SiteType.BIOFUEL_DEPOT,
        label: t("Biofuel Depot"),
        tooltip: t(
          "Entrepôt de biocarburants qui se situe uniquement en dehors de la France"
        ),
      },
      {
        type: SiteType.OIL_DEPOT,
        label: t("Oil Depot"),
        tooltip: t(
          "Entrepôt de biocarburants qui se situe uniquement en dehors de la France"
        ),
      },
      {
        type: SiteType.POWER_PLANT,
        label: t("Centrale électrique"),
        tooltip: t(
          "Centrale de production d'électricité qui utilise des biocarburants"
        ),
      },
      {
        type: SiteType.HEAT_PLANT,
        label: t("Centrale de chaleur"),
        tooltip: t(
          "Centrale de production de chaleur qui utilise des biocarburants"
        ),
      },
      {
        type: SiteType.COGENERATION_PLANT,
        label: t("Centrale de cogénération"),
        tooltip: t(
          "Centrale de production d'électricité et de chaleur qui utilise des biocarburants"
        ),
      },
      {
        type: SiteType.OTHER,
        label: t("Autre"),
      },
    ],
    [t]
  )
}

export const useDepotTypeLabels = () => {
  const depotTypeTranslations = useDepotTypeTranslations()

  return depotTypeTranslations.reduce(
    (acc, item) => ({
      ...acc,
      [item.type]: item.label,
    }),
    {} as Record<SiteType, string>
  )
}

type UseGetDepotTypeOptionsParams = {
  country?: Country
  labelFormatter?: (item: DepotTypeTranslationItem) => ReactNode
}
export const useGetDepotTypeOptions = ({
  country,
}: UseGetDepotTypeOptionsParams) => {
  const depotTypeTranslations = useDepotTypeTranslations()

  return useMemo(() => {
    let depotTypeOptions = depotTypeTranslations

    // If the country selected in the form is France, we have to remove Oil/Biofuel depot
    if (country?.code_pays === "FR") {
      depotTypeOptions = depotTypeOptions.filter(
        ({ type }) =>
          ![SiteType.OIL_DEPOT, SiteType.BIOFUEL_DEPOT].includes(type)
      )
    }

    // if the country selected in the form is not France, we have to remove EFS/EFPE/EFCA/Cogeneration/Heat/PowerPlant
    if (country && country.code_pays !== "FR") {
      depotTypeOptions = depotTypeOptions.filter(
        ({ type }) =>
          ![
            SiteType.EFS,
            SiteType.EFCA,
            SiteType.EFPE,
            SiteType.COGENERATION_PLANT,
            SiteType.HEAT_PLANT,
            SiteType.POWER_PLANT,
          ].includes(type)
      )
    }

    return depotTypeOptions.map(({ label, tooltip, type }) => ({
      label: tooltip ? (
        <span
          style={{
            display: "flex",
            alignItems: "center",
            columnGap: "var(--spacing-xs)",
          }}
        >
          {label}
          <Tooltip title={tooltip} style={{ display: "flex" }}>
            <InfoCircle color="#a4a4a4" size={16} />
          </Tooltip>
        </span>
      ) : (
        label
      ),
      value: type,
    }))
  }, [country, depotTypeTranslations])
}

export const useOwnerShipTypeOptions = () => {
  const { t } = useTranslation()

  return useMemo(
    () => [
      { value: OwnershipType.OWN, label: t("Propre") },
      { value: OwnershipType.THIRD_PARTY, label: t("Tiers") },
      { value: OwnershipType.PROCESSING, label: t("Processing") },
    ],
    [t]
  )
}
