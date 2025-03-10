import { findProductionSites } from "common/api"
import useEntity from "common/hooks/entity"
import { ProductionSite } from "common/types"
import * as norm from "common/utils/normalizers"
import Alert from "common/components/alert"
import Autocomplete from "common/components/autocomplete"
import { Button, MailTo } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Dialog } from "common/components/dialog"
import { useForm } from "common/components/form"
import { AlertTriangle, Return, Send } from "common/components/icons"
import { TextInput } from "common/components/input"
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
    <Dialog onClose={onClose}>
      <header>
        <h1>
          <Trans>Envoyer la demande d'agrément</Trans>
        </h1>
      </header>

      <main>
        <section>
          <p>
            <Trans>
              Votre fichier est valide. Vous pouvez maintenant transmettre la
              demande d'agrément double comptage à la DGEC pour une vérification
              approfondie.
            </Trans>
          </p>
        </section>
        <section>
          {fileData.has_dechets_industriels && (
            <DechetIndustrielAlert mailToIsButton={true} />
          )}
        </section>
        <section>
          <TextInput label={t("Producteur")} value={entity.name} readOnly />
          <Autocomplete
            required
            label={t("Site de production")}
            getOptions={(query) => findProductionSites(query, entity.id)}
            normalize={norm.normalizeProductionSite}
            {...bind("productionSite")}
          />
          {fileData.has_dechets_industriels && (
            <Checkbox
              label={t(
                "Je confirme avoir envoyé par email le formulaire mentionné ci-dessus. "
              )}
              required={true}
              {...bind("formSent")}
            />
          )}
        </section>

        {error && (
          <section ref={refToScroll}>
            <Alert
              variant="warning"
              icon={AlertTriangle}
              style={{ display: "inline-block" }}
            >
              {error}
            </Alert>
          </section>
        )}
      </main>

      <footer>
        <Button
          loading={addApplication.loading}
          icon={Send}
          label={t("Envoyer la demande")}
          variant="primary"
          disabled={
            addApplication.loading ||
            !value.productionSite ||
            (fileData.has_dechets_industriels && !value.formSent)
          }
          action={saveApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
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
      <Button variant="link" action={goToProductionSites}>
        {"→ "}
        {t(`Editer le site de production {{productionSiteName}}`, {
          productionSiteName,
        })}
      </Button>
    </>
  )
}

export const MailToDialog = ({
  onClose,
  fileData,
}: {
  onClose: () => void
  fileData: DoubleCountingFileInfo
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const dechetsIndustrielMessage = fileData.has_dechets_industriels
    ? "%0D%0A-%20le%20questionnaire%20de%20processus%20de%20validation%20des%20mati%C3%A8res%20premieres%20rempli%20pour%20les%20d%C3%A9chets%20industriels%20mentionn%C3%A9s"
    : ""
  const bodyMessage = `Mesdames%2C%20Messieurs%2C%0D%0A%0D%0AJe%20vous%20faire%20parvenir%20le%20dossier%20de%20demande%20de%20reconnaissance%20au%20Double%20Comptage%20pour%20notre%20soci%C3%A9t%C3%A9.%0D%0AJ'ai%20joint%20%20%3A%0D%0A-%20le%20fichier%20Excel%20apr%C3%A8s%20validation%20avec%20la%20plateforme%20CarbuRe${dechetsIndustrielMessage}%0D%0A%0D%0ABien%20cordialement`

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Envoi du dossier double comptage")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: "left" }}>
            {t(
              "Votre fichier est valide. Vous pouvez le transmettre par email à la DGEC pour une vérification approfondie à l'adresse carbure@beta.gouv.fr en cliquant ci-dessous : "
            )}
          </p>
          {fileData.has_dechets_industriels && <DechetIndustrielAlert />}
          <MailTo
            user="carbure"
            host="beta.gouv.fr"
            subject={`[CarbuRe - Double comptage] Demande de ${entity.name}`}
            body={bodyMessage}
          >
            <Trans>Envoyer la demande par email</Trans>
          </MailTo>
        </section>
      </main>

      <footer>
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}
