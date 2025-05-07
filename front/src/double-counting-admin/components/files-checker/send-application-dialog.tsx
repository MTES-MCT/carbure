import { findProducers, findProductionSites } from "common/api"
import useEntity from "common/hooks/entity"
import { ProductionSite, EntityPreview } from "common/types"
import * as norm from "common/utils/normalizers"
import { Notice } from "common/components/notice"
import { Autocomplete } from "common/components/autocomplete2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useForm } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { adminAddDoubleCountingApplication } from "double-counting-admin/api"
import React, { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import FileApplicationInfo from "./file-application-info"
import { DoubleCountingFileInfo } from "../../../double-counting/types"
import { ReplaceApplicationDialog } from "../../../double-counting/components/application-checker/replace-application-dialog"
import { HttpError } from "common/services/api-fetch"

export type SendApplicationAdminDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const SendApplicationAdminDialog = ({
  file,
  fileData,
  onClose,
}: SendApplicationAdminDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const [error, setError] = useState<React.ReactNode | undefined>(undefined)
  const { value, bind } = useForm<ProductionForm>(defaultProductionForm)
  const notify = useNotify()
  const notifyError = useNotifyError()
  const navigate = useNavigate()

  const addApplication = useMutation(adminAddDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess() {
      onClose()
      notify(t("Le dossier a été ajouté !"), { variant: "success" })
      navigate({
        pathname: "/org/9/double-counting",
      })
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
      } else if (errorCode === "AGREEMENT_NOT_FOUND") {
        setError(
          t(
            'Le numéro "{{certificateId}}" ne correspond à aucun agrément actif.',
            { agreementId: value.certificate_id }
          )
        )
      } else if (errorCode === "PRODUCTION_SITE_ADDRESS_UNDEFINED") {
        setError(<MissingAddress productionSiteId={value.productionSite?.id} />)
      } else {
        notifyError(err, t("Impossible d'ajouter le dossier"))
      }
    },
  })

  const saveApplication = async (shouldReplace = false) => {
    if (!value.productionSite || !value.producer) return
    setError(undefined)

    addApplication.execute(
      entity.id,
      value.productionSite.id,
      value.producer.id,
      file,
      value.certificate_id,
      shouldReplace
    )
  }

  const producer = value.producer instanceof Object ? value.producer.id : undefined // prettier-ignore

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>
            <Trans>Ajout du dossier double comptage</Trans>
          </Dialog.Title>
          <Dialog.Description>
            <FileApplicationInfo fileData={fileData} />
          </Dialog.Description>
        </>
      }
      footer={
        <Button
          loading={addApplication.loading}
          iconId="ri-send-plane-line"
          disabled={
            addApplication.loading || !value.productionSite || !value.producer
          }
          onClick={() => saveApplication()}
        >
          {t("Ajouter le dossier")}
        </Button>
      }
    >
      <Autocomplete
        required
        label={t("Producteur")}
        getOptions={findProducers}
        normalize={norm.normalizeEntityPreview}
        {...bind("producer")}
      />
      <Autocomplete
        required
        label={t("Site de production")}
        getOptions={(query) => findProductionSites(query, producer)}
        normalize={norm.normalizeProductionSite}
        {...bind("productionSite")}
      />
      <TextInput
        label={t("N° d'agrément lié à ce dossier")}
        placeholder={t("Laisser vide si nouvelle demande")}
        {...bind("certificate_id")}
      />

      {error && (
        <section>
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
  producer: undefined as EntityPreview | undefined,
  certificate_id: undefined as string | undefined,
}

type ProductionForm = typeof defaultProductionForm

function MissingAddress({
  productionSiteId,
}: {
  productionSiteId: number | undefined
}) {
  const { t } = useTranslation()
  return (
    <>
      {t(
        "L'adresse, la ville ou le code postal du site de production n'est pas renseignée. Veuillez l'ajouter dans les informations liées à la société."
      )}
      <Button
        customPriority="link"
        linkProps={{
          to: `/admin/producers/productionsite/${productionSiteId}/change`,
        }}
      >
        <Trans>Editer le site de production</Trans>
      </Button>
    </>
  )
}
