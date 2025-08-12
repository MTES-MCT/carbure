import { useMutation, useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { UnitType } from "biomethane/types"
import {
  createProductionUnit,
  getProductionUnit,
  updateProductionUnit,
} from "biomethane/api"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"

export const useProductionUnit = () => {
  const entity = useEntity()
  const query = useQuery(getProductionUnit, {
    key: "production-unit",
    params: [entity.id],
  })

  return query
}

export const useUnitTypeOptions = () => {
  const { t } = useTranslation()
  return [
    {
      label: t("Agricole autonome"),
      value: UnitType.AGRICULTURAL_AUTONOMOUS,
    },
    {
      label: t("Agricole territorial"),
      value: UnitType.AGRICULTURAL_TERRITORIAL,
    },
    {
      label: t("Industriel territorial"),
      value: UnitType.INDUSTRIAL_TERRITORIAL,
    },
    {
      label: t("Déchets ménagers et biodéchets"),
      value: UnitType.HOUSEHOLD_WASTE_BIOWASTE,
    },
    {
      label: t("ISDND"),
      value: UnitType.ISDND,
    },
  ]
}

/**
 * @param hasProductionUnit if true, the mutation will update the existing production unit, otherwise it will create a new one
 */
export const useMutateProductionUnit = (hasProductionUnit: boolean = false) => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation(
    hasProductionUnit
      ? (data) => updateProductionUnit(entity.id, data)
      : (data) => createProductionUnit(entity.id, data),
    {
      invalidates: ["production-unit"],
      onSuccess: () => {
        notify(t("L'unité de production a bien été mise à jour."), {
          variant: "success",
        })
      },
      onError: (e) => {
        notifyError(e)
      },
    }
  )

  return mutation
}
