import { useMutation, useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  createProductionUnit,
  getProductionUnit,
  updateProductionUnit,
  getDigestateStorages,
  addDigestateStorage,
  updateDigestateStorage,
  deleteDigestateStorage,
} from "./api"
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

// Digestate Storage hooks
export const useDigestateStorages = () => {
  const entity = useEntity()
  const query = useQuery(getDigestateStorages, {
    key: "digestate-storages",
    params: [entity.id],
  })

  return query
}

export const useAddDigestateStorage = () => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation((data) => addDigestateStorage(entity.id, data), {
    invalidates: ["digestate-storages"],
    onSuccess: () => {
      notify(t("Le stockage de digestat a bien été ajouté."), {
        variant: "success",
      })
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  return mutation
}

export const useUpdateDigestateStorage = () => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation(
    ({ id, data }: { id: number; data: any }) =>
      updateDigestateStorage(entity.id, id, data),
    {
      invalidates: ["digestate-storages"],
      onSuccess: () => {
        notify(t("Le stockage de digestat a bien été mis à jour."), {
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

export const useDeleteDigestateStorage = () => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation(
    (id: number) => deleteDigestateStorage(entity.id, id),
    {
      invalidates: ["digestate-storages"],
      onSuccess: () => {
        notify(t("Le stockage de digestat a bien été supprimé."), {
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
