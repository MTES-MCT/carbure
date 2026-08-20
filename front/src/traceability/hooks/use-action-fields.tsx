import { useTranslation } from "react-i18next"

import { FormManager } from "common/components/form2"
import { DateInput, NumberInput, TextInput } from "common/components/inputs2"
import { Select } from "common/components/selects2"
import { EntityManager } from "common/hooks/entity"
import { Action, ActionShippingMethod } from "traceability/types"

export type ActionFieldOptions = {
  form: FormManager<Partial<Action>>
  readOnly?: boolean
  label?: string
}

export type ActionField = {
  key: keyof Partial<Action>
  label: string
  field: (options: ActionFieldOptions) => React.ReactNode
  condition?: (entity: EntityManager) => boolean
}

export function useActionFields() {
  const { t } = useTranslation()

  return {
    holder: {
      key: "holder",
      label: t("Détenteur"),
      field: ({ form, ...props }) => (
        <NumberInput {...props} {...form.bind("holder")} />
      ),
    },

    material: {
      key: "material",
      label: t("Matière"),
      field: ({ form, ...props }) => (
        <NumberInput {...props} {...form.bind("material")} />
      ),
    },

    quantity: {
      key: "quantity",
      label: t("Quantité"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("quantity")} />
      ),
    },

    site: {
      key: "site",
      label: t("Site"),
      field: ({ form, ...props }) => (
        <NumberInput {...props} {...form.bind("site")} />
      ),
    },

    pos_id: {
      key: "pos_id",
      label: t("N° de POS"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("pos_id")} />
      ),
    },

    shipping_date: {
      key: "shipping_date",
      label: t("Date d'expédition"),
      field: ({ form, ...props }) => (
        <DateInput {...props} {...form.bind("shipping_date")} />
      ),
    },

    shipping_distance: {
      key: "shipping_distance",
      label: t("Distance de livraison"),
      field: ({ form, ...props }) => (
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
      field: ({ form, ...props }) => (
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
      field: ({ form, ...props }) => (
        <DateInput {...props} {...form.bind("working_date")} />
      ),
    },

    ei: {
      key: "ei",
      label: t("EI"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("ei")} />
      ),
    },

    ep: {
      key: "ep",
      label: t("EP"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("ep")} />
      ),
    },

    etd: {
      key: "etd",
      label: t("ETD"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("etd")} />
      ),
    },

    eu: {
      key: "eu",
      label: t("EU"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("eu")} />
      ),
    },

    eccs: {
      key: "eccs",
      label: t("ECCS"),
      field: ({ form, ...props }) => (
        <TextInput {...props} {...form.bind("eccs")} />
      ),
    },
  } satisfies Record<string, ActionField>
}
