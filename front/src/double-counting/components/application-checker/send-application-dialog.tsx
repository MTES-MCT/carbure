import { findProductionSites } from "common/api"
import useEntity from "common/hooks/entity"
import { ProductionSite } from "common/types"
import * as norm from "common/utils/normalizers"
import { Notice } from "common/components/notice"
import { Autocomplete } from "common/components/autocomplete2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useForm } from "common/components/form"
import { TextInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useCloseAllPortals, usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { producerAddDoubleCountingApplication } from "double-counting/api"
import React, { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { DoubleCountingFile, DoubleCountingFileInfo } from "../../types"
import { ReplaceApplicationDialog } from "./replace-application-dialog"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { HttpError } from "common/services/api-fetch"
import { compact } from "common/utils/collection"

export type SendApplicationProducerDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  extraFiles: DoubleCountingFile[]
  onSuccess: () => void
  onClose: () => void
}

export const SendApplicationProducerDialog = ({
  file,
  fileData,
  extraFiles,
  onSuccess,
  onClose,
}: SendApplicationProducerDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const portal = usePortal()
  const [error, setError] = useState<React.ReactNode | undefined>(undefined)
  const { value, bind } = useForm<ProductionForm>(defaultProductionForm)
  const { refToScroll } = useScrollToRef(!!error)

  const notify = useNotify()
  const notifyError = useNotifyError()

  const addApplication = useMutation(producerAddDoubleCountingApplication, {
    invalidates: ["dc-agreements"],
    onSuccess() {
      onClose()
      onSuccess()
      notify(t("La demande a été envoyée !"), { variant: "success" })
    },
    onError(err) {
      const errorCode = (err as HttpError)?.data?.message

      if (errorCode === "APPLICATION_ALREADY_EXISTS") {
        portal((close) => (
          <ReplaceApplicationDialog
            onReplace={saveApplication}
            onClose={close}
          />
        ))
      } else if (errorCode === "AGREEMENT_ALREADY_EXISTS") {
        setError(
          t(
            "Un agrément existe déjà sur cette periode et pour ce site de production."
          )
        )
      } else if (errorCode === "PRODUCTION_SITE_ADDRESS_UNDEFINED") {
        setError(
          <MissingAddress productionSiteName={fileData.production_site} />
        )
      } else if (errorCode === "MISSING_INDUSTRIAL_WASTES_FILE") {
        setError(
          t(
            "La demande concerne des déchets industriels, merci de renseigner le questionnaire associé dans l'onglet 'Fichiers'."
          )
        )
      } else {
        notifyError(err, t("Impossible d'envoyer le dossier"))
      }
    },
  })

  const saveApplication = async (shouldReplace = false) => {
    if (!value.productionSite) return
    const files = compact(extraFiles.map((e) => e.file))
    setError(undefined)
    addApplication.execute(
      entity.id,
      entity.id,
      value.productionSite.id,
      file,
      files,
      shouldReplace
    )
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          <Trans>Envoyer la demande d'agrément</Trans>
        </Dialog.Title>
      }
      footer={
        <Button
          loading={addApplication.loading}
          iconId="ri-send-plane-line"
          disabled={
            addApplication.loading || !value.productionSite
            // || Boolean(value.productionSite.dc_reference)
          }
          onClick={() => saveApplication()}
        >
          {t("Envoyer la demande")}
        </Button>
      }
      fullWidth
    >
      <p>
        <Trans>
          Votre fichier est valide. Vous pouvez maintenant transmettre la
          demande d'agrément double comptage à la DGEC pour une vérification
          approfondie.
        </Trans>
      </p>

      <TextInput label={t("Producteur")} value={entity.name} disabled />
      <Autocomplete
        required
        label={t("Site de production")}
        getOptions={(query) => findProductionSites(query, entity.id)}
        normalize={norm.normalizeProductionSite}
        {...bind("productionSite")}
      />
      {error && (
        <section ref={refToScroll}>
          <Notice variant="warning" icon="ri-alert-line">
            {error}
          </Notice>
        </section>
      )}
    </Dialog>
  )
}

const defaultProductionForm = {
  productionSite: undefined as ProductionSite | undefined,
}

type ProductionForm = typeof defaultProductionForm

function MissingAddress({
  productionSiteName,
}: {
  productionSiteName: string
}) {
  const { t } = useTranslation()
  const entity = useEntity()
  const closeAll = useCloseAllPortals()

  return (
    <>
      {t(
        "L'adresse, la ville ou le code postal du site de production n'est pas renseignée. Veuillez l'ajouter dans les informations de votre site de production."
      )}
      <Button
        customPriority="link"
        linkProps={{
          to: `/org/${entity.id}/settings#production`,
          onClick: closeAll,
        }}
      >
        {"→ "}
        {t(`Editer le site de production {{productionSiteName}}`, {
          productionSiteName,
        })}
      </Button>
    </>
  )
}
