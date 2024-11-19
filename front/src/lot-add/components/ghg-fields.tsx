import { Fieldset, useFormContext } from "common/components/form"
import { BlankField, NumberInput, TextInput } from "common/components/input"
import { formatGHG, formatPercentage } from "common/utils/formatters"
import isAfter from "date-fns/isAfter"
import { useTranslation } from "react-i18next"
import { LotFormValue } from "./lot-form"
import useEntity from "carbure/hooks/entity"
import { EntityType, type Entity, SiteType } from "carbure/types"

interface GHGFieldsProps {
  readOnly?: boolean
}

export const EmissionFields = (props: GHGFieldsProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { bind, value } = useFormContext<LotFormValue>()

  return (
    <Fieldset small label={t("Émissions")}>
      <NumberInput
        required={value.feedstock?.category === "CONV"}
        label="EEC"
        hasTooltip
        title={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
        {...bind("eec")}
        {...props}
      />
      <NumberInput
        label="EL"
        hasTooltip
        title={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
        {...bind("el")}
        {...props}
      />
      <NumberInput
        required
        label="EP"
        hasTooltip
        title={t("Émissions résultant de la transformation")}
        {...bind("ep")}
        {...props}
      />
      <NumberInput
        required
        label="ETD"
        hasTooltip
        title={t("Émissions résultant du transport et de la distribution")}
        {...bind("etd")}
        {...props}
      />
      <NumberInput
        label="EU"
        hasTooltip
        title={t("Émissions résultant du carburant à l'usage")}
        {...bind("eu")}
        {...props}
      />

      <TextInput
        readOnly
        label="Total"
        value={formatGHG(value.ghg_total ?? 0)}
      />

      {canSeePlantGHG(entity, value, SiteType.POWER_PLANT) && (
        <NumberInput
          readOnly
          label="ECEL"
          hasTooltip
          title={t(
            "Émissions résultant de la combustion de biomasse pour la production d'électricité"
          )}
          {...bind("emission_electricity")}
          {...props}
        />
      )}

      {canSeePlantGHG(entity, value, SiteType.HEAT_PLANT) && (
        <NumberInput
          readOnly
          label="ECH"
          hasTooltip
          title={t(
            "Émissions résultant de la combustion de biomasse pour la production de chaleur"
          )}
          {...bind("emission_heat")}
          {...props}
        />
      )}
    </Fieldset>
  )
}

export const ReductionFields = (props: GHGFieldsProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { bind, value } = useFormContext<LotFormValue>()

  return (
    <Fieldset small label={t("Réductions")}>
      <NumberInput
        label="ESCA"
        hasTooltip
        title={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
        {...bind("esca")}
        {...props}
      />
      <NumberInput
        label="ECCS"
        hasTooltip
        title={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
        {...bind("eccs")}
        {...props}
      />
      <NumberInput
        label="ECCR"
        hasTooltip
        title={t("Réductions d'émissions dues au piégeage et à la substitution du carbone")} // prettier-ignore
        {...bind("eccr")}
        {...props}
      />
      <NumberInput
        label="EEE"
        hasTooltip
        title={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
        {...bind("eee")}
        {...props}
      />

      <BlankField />

      {isRedII(value.delivery_date) ? (
        <TextInput
          readOnly
          label={t("Réd. RED II")}
          value={formatPercentage(value.ghg_reduction_red_ii ?? 0)}
        />
      ) : (
        <TextInput
          readOnly
          label={t("Réd. RED I")}
          value={formatPercentage(value.ghg_reduction ?? 0)}
        />
      )}

      {canSeePlantGHG(entity, value, SiteType.POWER_PLANT) && (
        <TextInput
          readOnly
          label="Réd. élec."
          value={formatPercentage(value.total_reduction_electricity ?? 0)}
          {...props}
        />
      )}

      {canSeePlantGHG(entity, value, SiteType.HEAT_PLANT) && (
        <TextInput
          readOnly
          label="Réd. chaleur"
          value={formatPercentage(value.total_reduction_heat ?? 0)}
          {...props}
        />
      )}
    </Fieldset>
  )
}

export function isRedII(deliveryDate: string | undefined | null) {
  const date = deliveryDate ? new Date(deliveryDate) : new Date()
  return isAfter(date, JULY_FIRST_21)
}

// date where RED II took effect
const JULY_FIRST_21 = new Date("2021-07-01")

function canSeePlantGHG(entity: Entity, lot: LotFormValue, type: SiteType) {
  const isEntityAllowed =
    entity.entity_type === EntityType.PowerOrHeatProducer ||
    entity.entity_type === EntityType.Administration

  const isDeliverySiteForHeat =
    lot.delivery_site instanceof Object &&
    (lot.delivery_site.depot_type === type ||
      lot.delivery_site.depot_type === SiteType.COGENERATION_PLANT)

  return isEntityAllowed && isDeliverySiteForHeat
}
