import { useTranslation } from "react-i18next"
import { BiomethaneInjectionSite, NetworkType } from "./types"
import { saveInjectionSite, getInjectionSite } from "./api"
import { QueryOptions, useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useNotify, useNotifyError } from "common/components/notifications"

export const useGetInjectionNetworkTypesOption = () => {
  const { t } = useTranslation()

  return [
    {
      label: t("Transport"),
      value: NetworkType.TRANSPORT,
    },
    {
      label: t("Distribution"),
      value: NetworkType.DISTRIBUTION,
    },
  ]
}

export const useGetInjectionSite = (
  params: Omit<
    QueryOptions<BiomethaneInjectionSite | undefined, [number]>,
    "key" | "params"
  >
) => {
  const entity = useEntity()
  const query = useQuery(getInjectionSite, {
    ...params,
    key: "injection-site",
    params: [entity.id],
  })

  return query
}

export const useMutateInjectionSite = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const mutation = useMutation((data) => saveInjectionSite(entity.id, data), {
    invalidates: ["injection-site"],
    onSuccess: () => {
      notify(t("Le site d'injection a bien été mis à jour."), {
        variant: "success",
      })
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  return mutation
}
