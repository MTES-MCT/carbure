import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Divider } from "common/components/divider"
import { useHashMatch } from "common/components/hash-route"
import { Check, Download, Edit, Return, Send, Upload } from "common/components/icons"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import ChargePointsSampleMap from "elec-audit-admin/components/sample/sample-map"
import * as api from "elec-auditor/api"
import ApplicationStatus from "elec/components/application-status"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import ApplicationSummary from "./details-application-summary"
import { ElecChargePointsApplication, ElecMeterReadingsApplication } from "elec/types"
import { ElecAuditorApplicationDetails } from "elec-auditor/types"
import { useState } from "react"
import Stepper from "@codegouvfr/react-dsfr/Stepper"
import { FileInput } from "common/components/input"
import Form, { useForm } from "common/components/form"
import UploadReportSection from "./details-pending-upload"
import DownloadSampleSection from "./details-pending-download-sample"


interface ApplicationDetailsPendingProps {
  application: ElecAuditorApplicationDetails
  onDownloadSample: () => void

}
export const ApplicationDetailsPending = ({
  application,
  onDownloadSample
}: ApplicationDetailsPendingProps) => {
  const { t } = useTranslation()



  type IndicatorStep = "download-sample" | "upload-report" | "check-file"
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    {
      key: "download-sample",
      title: t("Récupération du retour de contrôle à remplir")
    },
    {
      key: "upload-report",
      title: t("Dépôt du fichier de résultat")
    },
    {
      key: "check-file",
      title: t("Vérification du fichier"),
    },
  ]

  const step: IndicatorStep = steps[currentStep].key as IndicatorStep

  function setStep(key: string) {
    setCurrentStep(steps.findIndex(step => step.key === key))
  }

  const downloadSample = () => {
    onDownloadSample()
    setStep("upload-report")
  }


  const reportUploaded = () => {
  }

  const sendReport = () => {

  }

  const Header = () => {
    return <section>
      <Stepper
        title={steps[currentStep].title}
        stepCount={steps.length}
        currentStep={currentStep + 1}
        nextTitle={steps[currentStep + 1]?.title}
      />
      <ApplicationSummary application={application} />
    </section>
  }

  return (
    <>


      {step === "download-sample" &&
        <DownloadSampleSection application={application} header={<Header />} onDownloadSample={downloadSample} />
      }
      {step === "upload-report" &&
        <UploadReportSection application={application} header={<Header />} onReportUploaded={reportUploaded} />
      }

      {step === "check-file" &&
        <>
          <main>
            <Header />
            <p>{t("Le fichier {{fileName}} comporte {{errorCount}} incohérences. Veuillez les corriger puis recharger à nouveau votre fichier.", { fileName: "XXXX", errorCount: "XXX" })}</p>
            <p>{t("Votre fichier d'audit {{fileName}} ne comporte aucune erreur.", { fileName: "XXXX" })}</p>
            <p>{t("Les informations peuvent être transmises à la DGEC.")}</p>
          </main>
          <footer>
            {step === "check-file" && <>
              <Button icon={Return} label={t("Importer un nouveau fichier")} variant="primary" action={() => setStep("upload-report")} />
              <Button icon={Send} label={t("Transmettre le résultat d'audit")} variant="primary" action={sendReport} />
            </>}
          </footer>
        </>
      }


    </>
  )
}




export default ApplicationDetailsPending

const ReportInfoAlert = () => {
  const { t } = useTranslation()

  return <Alert icon={Edit} variant="info" label={t("Précision sur les champs du tableau à remplir :")} >
    <p>
      <strong><Trans>Infrastructure de recharge installée à la localisation renseignée :</Trans></strong>
      <Trans>l'inspecteur confirme avoir trouvé le point de recharge à la localisation indiquée. Écrire "OUI" ou "NON" et passer aux étapes suivantes si l'infrastructure a été localisée ;</Trans>
    </p>

    <p>
      <strong><Trans>Identifiant renseigné visible à proximité immédiate de l'infrastructure :</Trans></strong>
      <Trans>l'inspecteur précise si l'identifiant renseigné est visible sur ou a proximité immédiate du point de recharge. La non visibilité de cet identifiant ne doit pas faire obstacle à la suite du contrôle si l'inspecteur est en mesure d'identifier les points de recharge par d'autres moyens (indication de l'aménageur/de l'opérateur par exemple). Écrire "OUI" ou "NON" ;</Trans>
    </p>

    <p>
      <strong><Trans>Point de contrôle type de courant :</Trans></strong>
      <Trans>l'inspecteur vérifie le type de courant délivré par le point de recharge (à partir du connecteur) et l'indique en écrivant "CC" ou "CA" </Trans>
    </p>

    <p>
      <strong><Trans>Numéro du certificat d'examen du type si différent :</Trans></strong>
      <Trans>l'inspecteur vérifie la correspondance entre le certificat d'examen du type déclaré par le demandeur (rappelé dans la colonne "no_mid") et celui du compteur installé dans le point de recharge. Il laisse la case vide en cas de correspondance ou indique le numéro du compteur installé si une différence est constatée ;</Trans>
    </p>

    <p>
      <strong><Trans>Date du relevé par l'intervenant :</Trans></strong>
      <Trans>la date de passage de l'inspecteur au format JJ/MM/AAAA ;</Trans>
    </p>
    <p>
      <strong><Trans>Énergie active totale relevée :</Trans></strong>
      <Trans>le relevé en kWh, au format XXXX,XX ;</Trans>
    </p>
    <p>
      <strong><Trans>Limite dans la mission de contrôle :</Trans></strong>
      <Trans>champ libre permettant d'indiquer tout circonstance ayant fait obstacle à la mission de contrôle.</Trans>
    </p>
  </Alert>
}