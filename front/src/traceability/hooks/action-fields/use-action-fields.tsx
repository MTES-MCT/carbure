import { useTranslation } from "react-i18next"

import { findEnabledEntities, findMaterials, findSites } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { FormManager } from "common/components/form2"
import {
  DateInput,
  DecimalInput,
  DecimalInputProps,
  NumberInput,
  TextInput,
} from "common/components/inputs2"
import { Select } from "common/components/selects2"
import { EntityManager } from "common/hooks/entity"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { getStepFromFractionDigits } from "common/utils/formatters"
import { SiteTypeEnum } from "api-schema"
import {
  Action,
  ActionHolder,
  ActionMaterial,
  ActionShippingMethod,
  ActionSite,
} from "traceability/types"
import {
  normalizeActionMaterial,
  normalizeActionSite,
} from "traceability/normalizers"
import { useGhgEmissionTitles } from "traceability/hooks/use-ghg-emission-titles"
import { quantityField } from "./quantity-field"
import {
  ACTION_EMISSIONS_UNIT,
  formatUnitActionDecimal,
} from "traceability/utils/formatters"

const ACTION_DECIMAL_STEP = getStepFromFractionDigits(3)

const ActionDecimalInput = (props: DecimalInputProps) => (
  <DecimalInput step={ACTION_DECIMAL_STEP} {...props} />
)

export type ActionFieldConfig = {
  form: FormManager<Partial<Action>>
  props: { readOnly?: boolean; label?: string }
  options?: Record<string, unknown>
}

export type ActionField = {
  key: keyof Partial<Action>
  label: string
  field: (config: ActionFieldConfig) => React.ReactNode
  condition?: (entity: EntityManager) => boolean
  options?: Record<string, unknown>
}

export type ActionFieldset = {
  legend: string
  fields: ActionField[]
}

export type ActionSiteFieldOptions = {
  siteTypes?: SiteTypeEnum[]
}

export function useActionFields() {
  const { t } = useTranslation()
  const emissionTitles = useGhgEmissionTitles()

  const pos_id: ActionField = {
    key: "pos_id",
    label: t("N° de POS"),
    field: ({ form, props }: ActionFieldConfig) => (
      <TextInput {...props} {...form.bind("pos_id")} />
    ),
  }

  return {
    holder: {
      key: "holder",
      label: t("Détenteur"),
      field: ({ form, props }) => {
        const bound = form.bind("holder")

        return (
          <Autocomplete<EntityPreview, ActionHolder>
            {...props}
            {...bound}
            defaultOptions={bound.value ? [bound.value] : undefined}
            getOptions={(query) => findEnabledEntities(query)}
            normalize={normalizeEntityPreview}
          />
        )
      },
    },

    material: {
      key: "material",
      label: t("Matière"),
      field: ({ form, props }) => {
        const bound = form.bind("material")

        return (
          <Autocomplete<ActionMaterial, ActionMaterial>
            {...props}
            {...bound}
            defaultOptions={bound.value ? [bound.value] : undefined}
            getOptions={findMaterials}
            normalize={normalizeActionMaterial}
          />
        )
      },
    },

    quantity: quantityField(),
    mass: quantityField("mass"),
    volume: quantityField("volume"),
    energy: quantityField("energy"),

    site: {
      key: "site",
      label: t("Site"),
      field: ({ form, props, options }) => {
        const bound = form.bind("site")
        const siteTypes = (options as ActionSiteFieldOptions)?.siteTypes

        return (
          <Autocomplete<ActionSite, ActionSite>
            {...props}
            {...bound}
            defaultOptions={bound.value ? [bound.value] : undefined}
            getOptions={(query) => findSites(query, siteTypes)}
            normalize={normalizeActionSite}
          />
        )
      },
    },

    pos_id,

    carbure_id: {
      ...pos_id,
      label: t("N° d'identifiant Carbure"),
    },

    certificate: {
      key: "certificate",
      label: t("N° de certificat"),
      field: ({ form, props }) => (
        <TextInput
          {...props}
          value={form.value.certificate?.certificate_id ?? ""}
        />
      ),
    },

    shipping_date: {
      key: "shipping_date",
      label: t("Date d'expédition"),
      field: ({ form, props }) => (
        <DateInput {...props} {...form.bind("shipping_date")} />
      ),
    },

    shipping_distance: {
      key: "shipping_distance",
      label: t("Distance de livraison"),
      field: ({ form, props }) => (
        <NumberInput
          hintText={t("En km")}
          {...props}
          {...form.bind("shipping_distance")}
        />
      ),
    },

    shipping_method: {
      key: "shipping_method",
      label: t("Mode de transport"),
      field: ({ form, props }) => (
        <Select
          {...props}
          {...form.bind("shipping_method")}
          variant="form"
          options={[
            { value: ActionShippingMethod.ROAD, label: t("Transport routier") },
            { value: ActionShippingMethod.PIPELINE, label: t("Pipeline") },
            { value: ActionShippingMethod.RAILROAD, label: t("Rail") },
            { value: ActionShippingMethod.SEA, label: t("Transport maritime") },
          ]}
        />
      ),
    },

    working_date: {
      key: "working_date",
      label: t("Date de référence"),
      field: ({ form, props }) => (
        <DateInput {...props} {...form.bind("working_date")} />
      ),
    },

    ei: {
      key: "ei",
      label: t("EI"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          hasTooltip
          title={emissionTitles.ei}
          {...form.bind("ei", { value: form.value.total_emissions?.ei })}
        />
      ),
    },

    ep: {
      key: "ep",
      label: t("EP"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          hasTooltip
          title={emissionTitles.ep}
          {...form.bind("ep", { value: form.value.total_emissions?.ep })}
        />
      ),
    },

    etd: {
      key: "etd",
      label: t("ETD"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          hasTooltip
          title={emissionTitles.etd}
          {...form.bind("etd", { value: form.value.total_emissions?.etd })}
        />
      ),
    },

    eu: {
      key: "eu",
      label: t("EU"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          hasTooltip
          title={emissionTitles.eu}
          {...form.bind("eu", { value: form.value.total_emissions?.eu })}
        />
      ),
    },

    eccs: {
      key: "eccs",
      label: t("ECCS"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          hasTooltip
          title={emissionTitles.eccs}
          {...form.bind("eccs", { value: form.value.total_emissions?.eccs })}
        />
      ),
    },

    total_emissions: {
      key: "total_emissions",
      label: t("Emissions"),
      field: ({ form, props }) => (
        <ActionDecimalInput
          {...props}
          readOnly
          value={form.value.total_emissions?.total ?? ""}
          readOnlyValue={formatUnitActionDecimal(
            form.value.total_emissions?.total,
            ACTION_EMISSIONS_UNIT
          )}
        />
      ),
    },
  } satisfies Record<string, ActionField>
}
