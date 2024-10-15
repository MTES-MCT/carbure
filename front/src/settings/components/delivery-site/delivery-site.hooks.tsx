import { Country, DepotType, OwnershipType } from "carbure/types"
import { InfoCircle } from "common/components/icons"
import Tooltip from "common/components/tooltip"
import { ReactNode, useMemo } from "react"
import { useTranslation } from "react-i18next"

export const useDeliverySiteFlags = (depotType?: DepotType) =>
  useMemo(
    () => ({
      isPowerPlant: depotType === DepotType.PowerPlant,
      isHeatPlant: depotType === DepotType.HeatPlant,
      isCogenerationPlant: depotType === DepotType.CogenerationPlant,
    }),
    [depotType]
  )

type DepotTypeTranslationItem = {
  type: DepotType
  label: string
  tooltip?: string
}

const useDepotTypeTranslations = () => {
  const { t } = useTranslation()

  return useMemo<DepotTypeTranslationItem[]>(
    () => [
      {
        type: DepotType.EFS,
        label: t("EFS"),
        tooltip: t("Entrepôt fiscal de stockage"),
      },
      {
        type: DepotType.EFPE,
        label: t("EFPE"),
        tooltip: t("Entrepôt fiscal de produits énergétiques"),
      },
      {
        type: DepotType.EFCA,
        label: t("EFCA"),
        tooltip: t("Entrepôt fiscal de carburants d'aviation"),
      },
      {
        type: DepotType.BiofuelDepot,
        label: t("Biofuel Depot"),
        tooltip: t(
          "Entrepôt de biocarburants qui se situe uniquement en dehors de la France"
        ),
      },
      {
        type: DepotType.OilDepot,
        label: t("Oil Depot"),
        tooltip: t(
          "Entrepôt de biocarburants qui se situe uniquement en dehors de la France"
        ),
      },
      {
        type: DepotType.PowerPlant,
        label: t("Centrale électrique"),
        tooltip: t(
          "Centrale de production d'électricité qui utilise des biocarburants"
        ),
      },
      {
        type: DepotType.HeatPlant,
        label: t("Centrale de chaleur"),
        tooltip: t(
          "Centrale de production de chaleur qui utilise des biocarburants"
        ),
      },
      {
        type: DepotType.CogenerationPlant,
        label: t("Centrale de cogénération"),
        tooltip: t(
          "Centrale de production d'électricité et de chaleur qui utilise des biocarburants"
        ),
      },
      {
        type: DepotType.OTHER,
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
    {} as Record<DepotType, string>
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
          ![DepotType.OilDepot, DepotType.BiofuelDepot].includes(type)
      )
    }

    // if the country selected in the form is not France, we have to remove EFS/EFPE/EFCA/Cogeneration/Heat/PowerPlant
    if (country && country.code_pays !== "FR") {
      depotTypeOptions = depotTypeOptions.filter(
        ({ type }) =>
          ![
            DepotType.EFS,
            DepotType.EFCA,
            DepotType.EFPE,
            DepotType.CogenerationPlant,
            DepotType.HeatPlant,
            DepotType.PowerPlant,
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
      { value: OwnershipType.Own, label: t("Propre") },
      { value: OwnershipType.ThirdParty, label: t("Tiers") },
      { value: OwnershipType.Processing, label: t("Processing") },
    ],
    [t]
  )
}
