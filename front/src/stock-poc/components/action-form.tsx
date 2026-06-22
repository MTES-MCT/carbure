import { Autocomplete } from "common/components/autocomplete2"
import { Form, useForm } from "common/components/form2"
import { NumberInput } from "common/components/inputs2"
import { Col } from "common/components/scaffold"
import { SelectDsfr } from "common/components/selects2"
import { findEnabledEntities } from "common/api"
import { EntityPreview } from "common/types"
import { normalizeEntityPreview } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { Action, ActionStatus, ActionType } from "../types"

export type ActionFormValue = {
  type?: ActionType
  status?: ActionStatus
  quantity?: number
  parent?: number
  owner?: EntityPreview
}

export const ActionForm = ({
  actions,
  initialValue = {},
  excludeActionId,
  formId = "stock-poc-action-form",
  onSubmit,
}: {
  actions: Action[]
  initialValue?: ActionFormValue
  excludeActionId?: number
  formId?: string
  onSubmit: (value: ActionFormValue) => void
}) => {
  const { t } = useTranslation()
  const form = useForm<ActionFormValue>(initialValue)
  const { value, bind, setField } = form

  const parentOptions = actions
    .filter((a) => a.id !== excludeActionId)
    .map((a) => ({
      value: String(a.id),
      label: `#${a.id} · ${a.type} · ${a.available} ${t("dispo")}`,
    }))

  return (
    <Form id={formId} form={form} onSubmit={() => onSubmit(value)}>
      <Col gap="md">
        <SelectDsfr
          label={t("Type d'action")}
          placeholder={t("Choisir un type")}
          required
          {...bind("type")}
          options={Object.values(ActionType)}
        />

        <SelectDsfr
          label={t("Statut")}
          placeholder={t("Aucun")}
          {...bind("status")}
          options={Object.values(ActionStatus)}
        />

        <NumberInput
          label={t("Quantité")}
          required
          min={0}
          step={0.01}
          {...bind("quantity")}
        />

        <SelectDsfr
          label={t("Action parente")}
          placeholder={t("Aucune (racine)")}
          {...bind("parent")}
          options={parentOptions}
          normalize={(o) => ({ value: Number(o.value), label: o.label })}
        />

        <Autocomplete
          label={t("Propriétaire (optionnel)")}
          placeholder={t("Entité courante par défaut")}
          getOptions={findEnabledEntities}
          normalize={normalizeEntityPreview}
          value={value.owner}
          onChange={(v) => setField("owner", v as EntityPreview)}
        />
      </Col>
    </Form>
  )
}
