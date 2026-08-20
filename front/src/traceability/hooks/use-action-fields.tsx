import { useTranslation } from "react-i18next"

import { FormManager } from "common/components/form2"
import { DateInput, NumberInput, TextInput } from "common/components/inputs2"
import { Select } from "common/components/selects2"
import { EntityManager } from "common/hooks/entity"
import {
  Action,
  ActionIndustry,
  ActionShippingMethod,
  ActionType,
} from "traceability/types"

export type ActionFieldOptions = FormManager<Partial<Action>> & {
  readOnly?: boolean
}

export type ActionField = {
  key: keyof Partial<Action>
  fieldset?: string
  field: (options: ActionFieldOptions) => React.ReactNode
  condition?: (entity: EntityManager) => boolean
}

export function useActionFields() {
  const { t } = useTranslation()

  return {
    id: {
      key: "id",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <NumberInput readOnly={readOnly} label={t("ID")} {...bind("id")} />
      ),
    },

    holder: {
      key: "holder",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <NumberInput
          readOnly={readOnly}
          label={t("Détenteur")}
          {...bind("holder")}
        />
      ),
    },

    industry: {
      key: "industry",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <Select
          variant="form"
          readOnly={readOnly}
          label={t("Industrie")}
          {...bind("industry")}
          options={[{ value: ActionIndustry.H2, label: t("H2") }]}
        />
      ),
    },

    material: {
      key: "material",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <NumberInput
          readOnly={readOnly}
          label={t("Matière")}
          {...bind("material")}
        />
      ),
    },

    quantity: {
      key: "quantity",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <TextInput
          readOnly={readOnly}
          label={t("Quantité")}
          {...bind("quantity")}
        />
      ),
    },

    site: {
      key: "site",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <NumberInput readOnly={readOnly} label={t("Site")} {...bind("site")} />
      ),
    },

    status: {
      key: "status",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <TextInput
          readOnly={readOnly}
          label={t("Statut")}
          {...bind("status")}
        />
      ),
    },

    pos_id: {
      key: "pos_id",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <TextInput
          readOnly={readOnly}
          label={t("N° de POS")}
          {...bind("pos_id")}
        />
      ),
    },

    type: {
      key: "type",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <Select
          variant="form"
          readOnly={readOnly}
          label={t("Type d'action")}
          {...bind("type")}
          options={[{ value: ActionType.INIT, label: t("INIT") }]}
        />
      ),
    },

    shipping_date: {
      key: "shipping_date",
      fieldset: t("Transport"),
      field: ({ bind, readOnly }) => (
        <DateInput
          readOnly={readOnly}
          label={t("Date d'expédition")}
          {...bind("shipping_date")}
        />
      ),
    },

    shipping_distance: {
      key: "shipping_distance",
      fieldset: t("Transport"),
      field: ({ bind, readOnly }) => (
        <NumberInput
          readOnly={readOnly}
          label={t("Distance de livraison")}
          hintText={t("En km")}
          {...bind("shipping_distance")}
        />
      ),
    },

    shipping_method: {
      key: "shipping_method",
      fieldset: t("Transport"),
      field: ({ bind, readOnly }) => (
        <Select
          variant="form"
          readOnly={readOnly}
          label={t("Mode de transport")}
          {...bind("shipping_method")}
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
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <DateInput
          readOnly={readOnly}
          label={t("Date de référence")}
          {...bind("working_date")}
        />
      ),
    },

    parent: {
      key: "parent",
      fieldset: t("Informations générales"),
      field: ({ bind, readOnly }) => (
        <NumberInput
          readOnly={readOnly}
          label={t("Action parente")}
          {...bind("parent")}
        />
      ),
    },

    ei: {
      key: "ei",
      fieldset: t("Émissions"),
      field: ({ bind, readOnly }) => (
        <TextInput readOnly={readOnly} label={t("EI")} {...bind("ei")} />
      ),
    },

    ep: {
      key: "ep",
      fieldset: t("Émissions"),
      field: ({ bind, readOnly }) => (
        <TextInput readOnly={readOnly} label={t("EP")} {...bind("ep")} />
      ),
    },

    etd: {
      key: "etd",
      fieldset: t("Émissions"),
      field: ({ bind, readOnly }) => (
        <TextInput readOnly={readOnly} label={t("ETD")} {...bind("etd")} />
      ),
    },

    eu: {
      key: "eu",
      fieldset: t("Émissions"),
      field: ({ bind, readOnly }) => (
        <TextInput readOnly={readOnly} label={t("EU")} {...bind("eu")} />
      ),
    },

    eccs: {
      key: "eccs",
      fieldset: t("Émissions"),
      field: ({ bind, readOnly }) => (
        <TextInput readOnly={readOnly} label={t("ECCS")} {...bind("eccs")} />
      ),
    },
  } satisfies Record<string, ActionField>
}
