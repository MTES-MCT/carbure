import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  BiomethaneContract,
  InstallationCategory,
  TariffReference,
} from "biomethane/pages/contract/types"
import { saveContract } from "biomethane/pages/contract/api"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { AnnualDeclarationResetDialog } from "biomethane/components/annual-declaration-reset-dialog"
import { useWatchedFields } from "biomethane/providers/watched-fields"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

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

export const useMutateContractInfos = (contract?: BiomethaneContract) => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const { hasWatchedFieldsChanged } = useWatchedFields<BiomethaneContract>()
  const { currentAnnualDeclaration } = useAnnualDeclaration()

  const mutation = useMutation(
    (data) =>
      saveContract(entity.id, data).then(() => {
        if (contract && hasWatchedFieldsChanged(contract, data)) {
          console.log("hasWatchedFieldsChanged")
          portal((close) => (
            <AnnualDeclarationResetDialog
              onClose={close}
              onConfirm={() => Promise.resolve()}
              annualDeclarationStatus={currentAnnualDeclaration?.status}
            />
          ))
        }
      }),
    {
      invalidates: [
        "contract-infos",
        "user-settings",
        "current-annual-declaration",
      ],
      onSuccess: () => {
        notify(t("Le contrat a bien été mis à jour."), { variant: "success" })
      },
      onError: (e) => {
        notifyError(e)
      },
    }
  )

  return mutation
}
