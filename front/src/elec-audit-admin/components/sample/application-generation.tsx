import { Stepper } from "@codegouvfr/react-dsfr/Stepper"
import { AxiosResponse } from "axios"
import useEntity from "carbure/hooks/entity"
import { EntityPreview } from "carbure/types"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import Checkbox from "common/components/checkbox"
import { Divider } from "common/components/divider"
import { Check, ChevronLeft, ChevronRight, Cross, Download, Send } from "common/components/icons"
import { Api } from "common/services/api"
import { ElecApplicationSample } from "elec-audit-admin/types"
import {
  ElecAuditApplicationStatus,
  ElecChargePointsApplicationDetails,
  ElecMeterReadingsApplicationDetails,
} from "elec/types"
import "leaflet-defaulticon-compatibility"
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css" // Re-uses images from ~leaflet package
import "leaflet/dist/leaflet.css"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import SampleGenerationForm from "./details-sample-generation-form"
import SampleSummary from "./details-sample-summary"
import ChargePointsSampleMap from "./sample-map"

export type GenerationState =
  | "generation"
  | "verification"
  | "email"
  | "confirmation"

interface ApplicationSampleGenerationProps {
  application:
  | ElecChargePointsApplicationDetails
  | ElecMeterReadingsApplicationDetails
  | undefined
  onAccept: (force: boolean) => void
  onReject: (force: boolean) => void
  onDownloadSample: () => void
  onStartAudit: (
    entityId: number,
    applicationId: number,
    chargePointIds: string[]
  ) => void
  summary: React.ReactNode
  emailIntro: string
  generateSampleQuery: (
    entityId: number,
    applicationId: number,
    percentage: number
  ) => Promise<AxiosResponse<Api<ElecApplicationSample>, any>>
  startAuditQueryLoading?: boolean
}
export const ApplicationSampleGeneration = ({
  application,
  onAccept,
  onReject,
  onDownloadSample,
  onStartAudit,
  summary,
  emailIntro,
  generateSampleQuery,
  startAuditQueryLoading,
}: ApplicationSampleGenerationProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const [confirmCheckbox, setConfirmCheckbox] = useState(false)
  const [sample, setSample] = useState<ElecApplicationSample | undefined>(
    undefined
  )

  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    {
      key: "generation",
      title: t("Génération de l'échantillon"),
    },
    {
      key: "verification",
      title: t("Audit des points de recharge"),
    },
    {
      key: "email",
      title: t("Génération de l'email "),
    },
    {
      key: "confirmation",
      title: t("Confirmation de l'envoie de l'ordre de contrôle"),
    },
  ]

  const step = steps[currentStep].key

  function setStep(key: string) {
    setCurrentStep(steps.findIndex((step) => step.key === key))
  }

  const startAudit = () => {
    if (!application || !sample) return
    onStartAudit(
      entity.id,
      application.id,
      sample.charge_points.map((cp) => cp.charge_point_id)
    )
  }

  const handleSampleGenerated = (sample: ElecApplicationSample) => {
    setSample(sample)
    setStep("verification")
  }

  const handleDownloadSample = async () => {
    await onDownloadSample()
    setStep("email")
  }

  return (
    <>
      <main>
        <section>
          <Stepper
            title={steps[currentStep].title}
            stepCount={steps.length}
            currentStep={currentStep + 1}
            nextTitle={steps[currentStep + 1]?.title}
          />
          {summary}
        </section>

        <Divider />

        <section>
          {step === "generation" && (
            <SampleGenerationForm
              power_total={application?.power_total ?? 0}
              applicationId={application?.id}
              generateSampleQuery={generateSampleQuery}
              onSampleGenerated={handleSampleGenerated}
            />
          )}

          {step === "verification" && sample && (
            <>
              <SampleSummary sample={sample} />
              <ChargePointsSampleMap chargePoints={sample.charge_points} />
              <SampleGenerationForm
                power_total={application?.power_total ?? 0}
                applicationId={application?.id}
                generateSampleQuery={generateSampleQuery}
                onSampleGenerated={handleSampleGenerated}
                retry
              />
            </>
          )}

          {step === "email" && <>
            <Alert icon={Send} variant="info" label={t("Action requise par l'administrateur pour poursuivre l'audit des points de recharge :")} >
              <ul>
                <li><Trans>Joindre le fichier téléchargé comportant l'échantillon des points de recharge à auditer</Trans></li>
                <li><Trans>Transmettre cet e-mail à l'aménageur</Trans></li>
              </ul>
            </Alert>
          </>}

          {step === "confirmation" && (
            <>
              <Checkbox
                value={confirmCheckbox}
                onChange={setConfirmCheckbox}
                label={t(
                  "Je confirme avoir envoyé l'ordre de contrôle par e-mail avec l'échantillon en pièce jointe."
                )}
              />
            </>
          )}

          {!entity.isAdmin &&
            application?.status === ElecAuditApplicationStatus.Pending && (
              <p>
                <i>{t("En attente de validation de la DGEC.")}</i>
              </p>
            )}
        </section>
      </main>

      <footer>
        {step === "generation" && (
          <>
            <Button
              icon={Check}
              label={t("Valider sans auditer")}
              variant="success"
              action={() => onAccept(true)}
            />
            <Button
              icon={Cross}
              label={t("Refuser sans auditer")}
              variant="danger"
              action={() => onReject(true)}
            />
          </>
        )}

        {step === "verification" && (
          <>
            <Button icon={Download} label={t("Télécharger l'échantillon")} variant="primary" action={handleDownloadSample} />
            <Button icon={ChevronRight} label={t("Suivant")} variant="secondary" action={() => setStep("email")} asideX />
          </>
        )}

        {step === "email" && application && <>
          <MailtoButton cpo={application.cpo} emailIntro={emailIntro} emailContacts={application.email_contacts!} onGenerate={() => setStep("confirmation")} />
          <Button icon={ChevronLeft} label={t("Précédent")} variant="secondary" action={() => setStep("verification")} asideX />
          <Button icon={ChevronRight} label={t("Suivant")} variant="secondary" action={() => setStep("confirmation")} asideY />

        </>}

        {step === "confirmation" && application && <>
          <Button icon={Send} label={t("Envoyer en audit")} variant="primary" action={startAudit} disabled={!confirmCheckbox || startAuditQueryLoading} loading={startAuditQueryLoading} />
          <Button icon={ChevronLeft} label={t("Précédent")} variant="secondary" action={() => setStep("email")} asideX />

        </>}
      </footer>
    </>
  )
}

interface MailtoButtonProps {
  cpo: EntityPreview
  emailIntro: string
  emailContacts: string[]
  onGenerate: () => void
}

const MailtoButton = ({
  cpo,
  emailContacts,
  emailIntro,
  onGenerate,
}: MailtoButtonProps) => {
  const { t } = useTranslation()
  const subject = `[CarbuRe - Audit Elec] Demande d'audit ${cpo.name}`
  const bodyIntro = emailIntro
  const bodyContent = `-%20Infrastructure%20de%20recharge%20install%C3%A9e%20%C3%A0%20la%20localisation%20renseign%C3%A9e%20%3A%0D%0Al'inspecteur%20confirme%20avoir%20trouv%C3%A9%20le%20point%20de%20recharge%20%C3%A0%20la%20localisation%20indiqu%C3%A9e.%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20et%20passer%20aux%20%C3%A9tapes%20suivantes%20si%20l'infrastructure%20a%20%C3%A9t%C3%A9%20localis%C3%A9e%20%3B%0D%0A%0D%0A-%20Identifiant%20renseign%C3%A9%20visible%20%C3%A0%20proximit%C3%A9%20imm%C3%A9diate%20de%20l'infrastructure%20%3A%0D%0Al'inspecteur%20pr%C3%A9cise%20si%20l'identifiant%20renseign%C3%A9%20est%20visible%20sur%20ou%20a%20proximit%C3%A9%20imm%C3%A9diate%20du%20point%20de%20recharge.%20La%20non%20visibilit%C3%A9%20de%20cet%20identifiant%20ne%20doit%20pas%20faire%20obstacle%20%C3%A0%20la%20suite%20du%20contr%C3%B4le%20si%20l'inspecteur%20est%20en%20mesure%20d'identifier%20les%20points%20de%20recharge%20par%20d'autres%20moyens%20(indication%20de%20l'am%C3%A9nageur%2Fde%20l'op%C3%A9rateur%20par%20exemple).%20%C3%89crire%20%22OUI%22%20ou%20%22NON%22%20%3B%0D%0A%0D%0A-%20Point%20de%20contr%C3%B4le%20type%20de%20courant%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20le%20type%20de%20courant%20d%C3%A9livr%C3%A9%20par%20le%20point%20de%20recharge%20(%C3%A0%20partir%20du%20connecteur)%20et%20l'indique%20en%20%C3%A9crivant%20%22CC%22%20ou%20%22CA%22%20%3B%0D%0A%0D%0A-%20Num%C3%A9ro%20du%20certificat%20d'examen%20du%20type%20si%20diff%C3%A9rent%20%3A%0D%0Al'inspecteur%20v%C3%A9rifie%20la%20correspondance%20entre%20le%20certificat%20d'examen%20du%20type%20d%C3%A9clar%C3%A9%20par%20le%20demandeur%20(rappel%C3%A9%20dans%20la%20colonne%20%22no_mid%22)%20et%20celui%20du%20compteur%20install%C3%A9%20dans%20le%20point%20de%20recharge.%20Il%20laisse%20la%20case%20vide%20en%20cas%20de%20correspondance%20ou%20indique%20le%20num%C3%A9ro%20du%20compteur%20install%C3%A9%20si%20une%20diff%C3%A9rence%20est%20constat%C3%A9e%20%3B%0D%0A%0D%0A-%20Date%20du%20relev%C3%A9%20par%20l'intervenant%20%3A%0D%0Ala%20date%20de%20passage%20de%20l'inspecteur%20au%20format%20JJ%2FMM%2FAAAA%20%3B%0D%0AEnergie%20active%20totale%20relev%C3%A9e%20%3A%20le%20relev%C3%A9%20en%20kWh%2C%20au%20format%20XXXX%2CXX%20%3B%0D%0ALimite%20dans%20la%20mission%20de%20contr%C3%B4le%20%3A%20champ%20libre%20permettant%20d'indiquer%20tout%20circonstance%20ayant%20fait%20obstacle%20%C3%A0%20la%20mission%20de%20contr%C3%B4le.%0D%0A%0D%0A`
  const bodyOutro = `Veuillez%20transmettre%20ce%20fichier%20%C3%A0%20votre%20auditeur%20officiel.%20Celui-ci%20pourra%20renvoyer%20le%20r%C3%A9sultat%20de%20cet%20audit%20%C3%A0%20l'adresse%20suivante%20%3A%0D%0A%0D%0Avalorisation-recharge%40developpement-durable.fr%0D%0A%0D%0A%0D%0AMerci%20de%20votre%20compr%C3%A9hension%2C%0D%0A%0D%0ABien%20%C3%A0%20vous%2C%0D%0A%0D%0AL'%C3%A9quipe%20CarbuRe`

  const mailto = `mailto:${emailContacts.join(",")}?subject=${encodeURIComponent(subject)}&body=${bodyIntro + bodyContent + bodyOutro}`

  return (
    <Button
      icon={Send}
      label={t("Générer l'email")}
      variant="primary"
      href={mailto}
      action={() => onGenerate()}
    />
  )
}

export default ApplicationSampleGeneration
