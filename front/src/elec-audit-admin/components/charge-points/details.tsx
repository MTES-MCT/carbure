import useEntity from "carbure/hooks/entity"
import { EntityPreview } from "carbure/types"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import Form from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross, Download, Return, Send } from "common/components/icons"
import { NumberInput, TextInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecChargePointsApplication, ElecAuditApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import ChargePointsApplicationAcceptDialog from "./accept-dialog"
import ChargePointsApplicationRejectDialog from "./reject-dialog"
import { useState } from "react"
import SampleGenerationForm from "./sample-generation-form"
import { Stepper } from "@codegouvfr/react-dsfr/Stepper";
import { Divider } from "common/components/divider"
import { ElecChargePointsApplicationSample } from "elec-audit-admin/types"


export type GenerationState = "generation" | "verification" | "email" | "confirmation"


export const ChargingPointsApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("application/:id")
  const [step, setStep] = useState<GenerationState>("generation")
  const [sample, setSample] = useState<ElecChargePointsApplicationSample | undefined>(undefined)
  const chargePointApplicationResponse = useQuery(api.getChargePointsApplicationDetails, {
    key: "audit-charge-points-application-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  const chargePointApplication = chargePointApplicationResponse.result?.data.data

  const startChargePointsApplicationAuditResponse = useMutation(api.startChargePointsApplicationAudit, {
    invalidates: ["audit-charge-points-application-details", "audit-charge-points-applications"],
    onSuccess() {
      notify(t("L'audit de l'inscription des {{count}} points de recharge a bien été initié.", { count: chargePointApplication?.charge_point_count }), { variant: "success" })
    },
    onError(err) {
      notifyError(err, t("Impossible d'initier l'audit de l'inscription des points de recharge"))
    },
  })

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const startAudit = () => {
    if (!chargePointApplication) return
    startChargePointsApplicationAuditResponse.execute(entity.id, chargePointApplication.id)
  }

  const acceptApplication = (force: boolean = false) => {
    if (!chargePointApplication) return
    portal((close) => (
      <ChargePointsApplicationAcceptDialog
        application={chargePointApplication}
        onClose={close}
        forceValidation={force}
        onValidated={closeDialog}
      />
    ))
  }

  const rejectApplication = (force: boolean = false) => {
    if (!chargePointApplication) return
    portal((close) => (
      <ChargePointsApplicationRejectDialog
        application={chargePointApplication}
        onClose={close}
        forceRejection={force}
        onRejected={closeDialog}

      />
    ))
  }

  const handleSampleGenerated = (sample: ElecChargePointsApplicationSample) => {
    setSample(sample)
    setStep("verification")
  }

  const downloadSample = async () => {
    if (!chargePointApplication) return
    const resp = api.downloadChargePointsSample(entity.id, chargePointApplication.id, true)
    setStep("email")
    return resp
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog} >
        <header>
          <ApplicationStatus status={chargePointApplication?.status} big />

          <h1>{t("Inscription de points de recharge")}</h1>
        </header>

        <main>

          <section>
            <ApplicationSummary application={chargePointApplication} />
          </section>
          <Divider />
          <section>
            {step === "generation" && <>
              <Stepper
                title={t("Génération de l'échantillon")}
                stepCount={4}
                currentStep={1}
                nextTitle={t("Audit des points de recharge")}
              />
              <SampleGenerationForm
                power_total={chargePointApplication?.power_total ?? 0}
                applicationId={chargePointApplication?.id}
                onSampleGenerated={handleSampleGenerated}
                buttonState="initial" />
            </>}
            {step === "verification" && sample && <>
              <Stepper
                title={t("Vérification de l'échantillon")}
                stepCount={4}
                currentStep={2}
                nextTitle={t("Génération de l’email ")}
              />
              <SampleSummary sample={sample} />
            </>}
          </section>
          <section>
            {!entity.isAdmin && chargePointApplication?.status === ElecAuditApplicationStatus.Pending && (
              <p><i>
                {t("En attente de validation de la DGEC.")}
              </i></p>
            )}
          </section>
          {chargePointApplication?.status === ElecAuditApplicationStatus.AuditInProgress && (

            <section>
              <Alert style={{ flexDirection: "column" }} variant="info"  >
                <p>
                  <Send />
                  <Trans>
                    Action requise par l'administrateur pour poursuivre l'audit de l'inscription des points de recharge :
                  </Trans>
                </p>
                <ul>
                  <li><Trans>Joindre le fichier téléchargé comportant l'échantillon des points de recharge à auditer</Trans></li>
                  <li><Trans>Transmettre cet e-mail à l'aménageur</Trans></li>
                </ul>

              </Alert>
            </section>
          )}
        </main>

        <footer>

          {step === "generation" && (
            <>
              {/* <Button icon={Send} label={t("Commencer l'audit")} variant="primary" action={startAudit} loading={startChargePointsApplicationAuditResponse.loading} /> */}
              <Button icon={Check} label={t("Valider sans auditer")} variant="success" action={() => acceptApplication(true)} />
              <Button icon={Cross} label={t("Refuser sans auditer")} variant="danger" action={() => rejectApplication(true)} />
            </>
          )}

          {step === "verification" && (
            <Button icon={Download} label={t("Télécharger l'échantillon")} variant="primary" action={downloadSample} />
          )}
          {/* <MailtoButton cpo={chargePointApplication.cpo} chargePointCount={chargePointApplication.charge_point_count} emailContacts={chargePointApplication.email_contacts!} />
              <Button icon={Check} label={t("Valide")} variant="success" action={acceptApplication} />
              <Button icon={Cross} label={t("Refuser")} variant="danger" action={rejectApplication} /> */}


        </footer>
        {chargePointApplicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}

const MailtoButton = ({ cpo, chargePointCount, emailContacts }: { cpo: EntityPreview, chargePointCount: number, emailContacts: string[] }) => {
  const { t } = useTranslation()
  const subject = `[CarbuRe - Audit Elec] Demande d'audit ${cpo.name}`
  const bodyIntro = `Bonjour%20${cpo.name}%0D%0A%0D%0A%0D%0AAfin%20de%20valider%20votre%20inscription%20de%20${chargePointCount}%20points%20de%20recharge%2C%20un%20audit%20doit%20%C3%AAtre%20men%C3%A9%20sur%20les%20points%20de%20recharge%20s%C3%A9lectionn%C3%A9s%20ci-joints.%0D%0A%0D%0A%0D%0AL'inspecteur%20doit%20remplir%20le%20tableau%20en%20respectant%20le%20format%20suivant%20%3A%0D%0A%0D%0A%0D%0A`
  const bodyContent = `-%20Infrastructure%20de%20recharge%20install%C3%A9e%20%C3%A0%20la%20localisation%20renseign%C3%A9e%20%3A%0D%0Al'inspecteur%20confirme%20avoir%20trouv%C3%A9%20le%20point%20de%20recharge%20%C3%A0%20la%20localisation%20indiqu%C3%A9e.%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20et%20passer%20aux%20%C3%A9tapes%20suivantes%20si%20l'infrastructure%20a%20%C3%A9t%C3%A9%20localis%C3%A9e%20%3B%0D%0A%0D%0A-%20Identifiant%20renseign%C3%A9%20visible%20%C3%A0%20proximit%C3%A9%20imm%C3%A9diate%20de%20l'infrastructure%20%3A%0D%0Al'inspecteur%20pr%C3%A9cise%20si%20l'identifiant%20renseign%C3%A9%20est%20visible%20sur%20ou%20a%20proximit%C3%A9%20imm%C3%A9diate%20du%20point%20de%20recharge.%20La%20non%20visibilit%C3%A9%20de%20cet%20identifiant%20ne%20doit%20pas%20faire%20obstacle%20%C3%A0%20la%20suite%20du%20contr%C3%B4le%20si%20l'inspecteur%20est%20en%20mesure%20d'identifier%20les%20points%20de%20recharge%20par%20d'autres%20moyens%20(indication%20de%20l'am%C3%A9nageur%2Fde%20l'op%C3%A9rateur%20par%20exemple).%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20%3B%0D%0A%0D%0A-%20Point%20de%20contr%C3%B4le%20type%20de%20courant%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20le%20type%20de%20courant%20d%C3%A9livr%C3%A9%20par%20le%20point%20de%20recharge%20(%C3%A0%20partir%20du%20connecteur)%20et%20l'indique%20en%20%C3%A9crivant%20%22CC%22%20ou%20%22CA%22%20%3B%0D%0A%0D%0A-%20Num%C3%A9ro%20du%20certificat%20d'examen%20du%20type%20si%20diff%C3%A9rent%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20la%20correspondance%20entre%20le%20certificat%20d'examen%20du%20type%20d%C3%A9clar%C3%A9%20par%20le%20demandeur%20(rappel%C3%A9%20dans%20la%20colonne%20%22no_mid%22)%20et%20celui%20du%20compteur%20install%C3%A9%20dans%20le%20point%20de%20recharge.%20Il%20laisse%20la%20case%20vide%20en%20cas%20de%20correspondance%20ou%20indique%20le%20num%C3%A9ro%20du%20compteur%20install%C3%A9%20si%20une%20diff%C3%A9rence%20est%20constat%C3%A9e%20%3B%0D%0A%0D%0A-%20Date%20du%20relev%C3%A9%20par%20l'intervenant%20%3A%0D%0Ala%20date%20de%20passage%20de%20l'inspecteur%20au%20format%20JJ%2FMM%2FAAAA%20%3B%0D%0AEnergie%20active%20totale%20relev%C3%A9e%20%3A%20le%20relev%C3%A9%20en%20kWh%2C%20au%20format%20XXXX%2CXX%20%3B%0D%0ALimite%20dans%20la%20mission%20de%20contr%C3%B4le%20%3A%20champ%20libre%20permettant%20d'indiquer%20tout%20circonstance%20ayant%20fait%20obstacle%20%C3%A0%20la%20mission%20de%20contr%C3%B4le.%0D%0A%0D%0A`
  const bodyOutro = `Veuillez%20transmettre%20ce%20fichier%20%C3%A0%20votre%20auditeur%20officiel.%20Celui-ci%20pourra%20renvoyer%20le%20r%C3%A9sultat%20de%20cet%20audit%20%C3%A0%20l'adresse%20suivante%20%3A%0D%0A%0D%0Avalorisation-recharge%40developpement-durable.fr%0D%0A%0D%0A%0D%0AMerci%20de%20votre%20compr%C3%A9hension%2C%0D%0A%0D%0ABien%20%C3%A0%20vous%2C%0D%0A%0D%0AL'%C3%A9quipe%20CarbuRe`

  const mailto = `mailto:${emailContacts.join(',')}?subject=${encodeURIComponent(subject)}&body=${bodyIntro + bodyContent + bodyOutro}`

  return <Button icon={Send} label={t("Générer l'email")} variant="secondary" href={mailto} />

}


const SampleSummary = ({ sample }: { sample: ElecChargePointsApplicationSample }) => {
  const { t } = useTranslation()

  return <>
    <strong>Échantillon</strong>

    <Form
      variant="columns"
    >
      <NumberInput
        readOnly
        label={t("Date de la demande")}
        value={sample.charge_points.length}
      />

      <TextInput
        readOnly
        label={t("Pourcentage de puissance installée à auditeur")}
        value={sample.percentage + "%"}

      />
    </Form>
  </>
}


const ApplicationSummary = ({ application }: { application: ElecChargePointsApplication | undefined }) => {
  const { t } = useTranslation()

  return <Form
    variant="columns"
  >

    <TextInput
      readOnly
      label={t("Date de la demande")}
      value={application ? formatDate(application.application_date) : "..."}
    />

    <TextInput
      readOnly
      label={t("Aménageur")}
      value={application?.cpo.name || "..."}

    />

    <TextInput
      readOnly
      label={t("Puissance cumulée (kW)")}
      value={application ? formatNumber(Math.round(application.power_total)) : "..."}

    />

    <TextInput
      readOnly
      label={t("Points de recharge")}
      value={application ? formatNumber(application.charge_point_count) : "..."}
    />


  </Form>
}


export default ChargingPointsApplicationDetailsDialog
