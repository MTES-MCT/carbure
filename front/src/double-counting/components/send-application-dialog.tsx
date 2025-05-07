import { findProductionSites } from "common/api"
import useEntity from "common/hooks/entity"
import { ProductionSite } from "common/types"
import * as norm from "common/utils/normalizers"
import { Notice } from "common/components/notice"
import { Autocomplete } from "common/components/autocomplete2"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useForm } from "common/components/form"
import { Checkbox, TextInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { producerAddDoubleCountingApplication } from "double-counting/api"
import React, { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { DoubleCountingFileInfo } from "../types"
import { DechetIndustrielAlert } from "./application-checker/industrial-waste-alert"
import { ReplaceApplicationDialog } from "./application-checker/replace-application-dialog"
import { useNavigate } from "react-router-dom"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { HttpError } from "common/services/api-fetch"

export type SendApplicationProducerDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const SendApplicationProducerDialog = ({
  file,
  fileData,
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
          <MissingAddress
            onClose={onClose}
            productionSiteName={fileData.production_site}
          />
        )
      } else {
        notifyError(err, t("Impossible d'envoyer le dossier"))
      }
    },
  })

  const saveApplication = async (shouldReplace = false) => {
    if (!value.productionSite) return
    setError(undefined)
    addApplication.execute(
      entity.id,
      entity.id,
      value.productionSite.id,
      file,
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
            addApplication.loading ||
            !value.productionSite ||
            (fileData.has_dechets_industriels && !value.formSent) ||
            Boolean(value.productionSite.dc_reference)
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
      {fileData.has_dechets_industriels && <DechetIndustrielAlert />}

      <TextInput label={t("Producteur")} value={entity.name} disabled />
      <Autocomplete
        required
        label={t("Site de production")}
        getOptions={(query) => findProductionSites(query, entity.id)}
        normalize={norm.normalizeProductionSite}
        {...bind("productionSite")}
        state={value.productionSite?.dc_reference ? "error" : "default"}
        stateRelatedMessage={
          value.productionSite?.dc_reference ? (
            <>
              {t("Le site contient déjà un numéro d'agrément en cours")} (
              {value.productionSite.dc_reference})
            </>
          ) : undefined
        }
      />
      {fileData.has_dechets_industriels && (
        <Checkbox
          label={t(
            "Je confirme avoir envoyé par email le formulaire mentionné ci-dessus. "
          )}
          {...bind("formSent")}
        />
      )}

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
  formSent: false as boolean,
}

type ProductionForm = typeof defaultProductionForm

function MissingAddress({
  productionSiteName,
  onClose,
}: {
  productionSiteName: string
  onClose: () => void
}) {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()

  const goToProductionSites = () => {
    onClose()
    navigate(`/org/${entity.id}/settings#production`)
  }

  return (
    <>
      {t(
        "L'adresse, la ville ou le code postal du site de production n'est pas renseignée. Veuillez l'ajouter dans les informations de votre site de production."
      )}
      <Button customPriority="link" onClick={goToProductionSites}>
        {"→ "}
        {t(`Editer le site de production {{productionSiteName}}`, {
          productionSiteName,
        })}
      </Button>
    </>
  )
}
