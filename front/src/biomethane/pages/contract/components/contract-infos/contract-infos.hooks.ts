import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  InstallationCategory,
  TariffReference,
} from "biomethane/pages/contract/types"
import { saveContract } from "biomethane/pages/contract/api"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"

export const useTariffReferenceOptions = () => {
  const { t } = useTranslation()

  return [
    {
      label: t("2011 - Arrêté du 23/11/2011"),
      value: TariffReference.Value2011,
    },
    {
      label: t("2020 - Arrêté du 23/11/2020"),
      value: TariffReference.Value2020,
    },
    {
      label: t("2021 - Arrêté du 13/12/2021"),
      value: TariffReference.Value2021,
    },
    {
      label: t("2023 - Arrêté du 10/06/2023"),
      value: TariffReference.Value2023,
    },
  ]
}

export const useInstallationCategoryOptions = () => {
  const { t } = useTranslation()
  return [
    {
      label: t(
        "Méthanisation en digesteur de produits ou déchets non dangereux, hors matières résultant du traitement des eaux usées urbaines ou industrielles"
      ),
      value: InstallationCategory.INSTALLATION_CATEGORY_1,
    },
    {
      label: t(
        "Méthanisation en digesteur de produits ou déchets non dangereux, y compris des matières résultant du traitement des eaux usées urbaines ou industrielles"
      ),
      value: InstallationCategory.INSTALLATION_CATEGORY_2,
    },
    {
      label: t(
        "Installations de stockage de déchets non dangereux à partir de déchets ménagers et assimilés"
      ),
      value: InstallationCategory.INSTALLATION_CATEGORY_3,
    },
  ]
}

/**
 * @param hasContract if true, the mutation will create a new contract, otherwise it will update the existing one
 */
export const useMutateContractInfos = () => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation((data) => saveContract(entity.id, data), {
    invalidates: ["contract-infos", "user-settings"],
    onSuccess: () => {
      notify(t("Le contrat a bien été mis à jour."), { variant: "success" })
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  return mutation
}
