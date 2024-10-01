import Stepper from "@codegouvfr/react-dsfr/Stepper"
import { UploadCheckReportInfo } from "carbure/types"
import {
  ElecAuditorApplicationDetails,
  ElecAuditorUploadCheckReportInfo,
} from "elec-auditor/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import ApplicationSummary from "./details-application-summary"
import CheckReportSection from "./details-pending-check"
import DownloadSampleSection from "./details-pending-download-sample"
import ReportErrorsSection from "./details-pending-report-errors"
import ReportValidSection from "./details-pending-report-valid"

interface ApplicationDetailsPendingProps {
  application: ElecAuditorApplicationDetails
  onDownloadSample: () => void
  onReportAccepted: () => void
}
export const ApplicationDetailsPending = ({
  application,
  onDownloadSample,
  onReportAccepted,
}: ApplicationDetailsPendingProps) => {
  const { t } = useTranslation()

  type IndicatorStep = "download-sample" | "check-report" | "report-checked"
  const [currentStep, setCurrentStep] = useState(0)
  const [checkInfo, setCheckInfo] = useState<
    ElecAuditorUploadCheckReportInfo | undefined
  >()
  const [checkedFile, setCheckedFile] = useState<File | undefined>()

  const steps = [
    {
      key: "download-sample",
      title: t("Récupération du retour de contrôle à remplir"),
    },
    {
      key: "check-report",
      title: t("Dépôt du fichier de résultat"),
    },
    {
      key: "report-checked",
      title: t("Vérification du fichier"),
    },
  ]

  const step: IndicatorStep = steps[currentStep]?.key as IndicatorStep

  function setStep(key: string) {
    setCurrentStep(steps.findIndex((step) => step.key === key))
  }

  const downloadSample = () => {
    onDownloadSample()
  }
  const handleSampleDownloaded = () => {
    setStep("check-report")
  }

  const reportChecked = (file: File, info: UploadCheckReportInfo) => {
    setCheckInfo(info)
    setCheckedFile(file)
    setStep("report-checked")
  }

  const Header = () => {
    return (
      <section>
        <Stepper
          title={steps[currentStep]?.title}
          stepCount={steps.length}
          currentStep={currentStep + 1}
          nextTitle={steps[currentStep + 1]?.title}
        />
        <ApplicationSummary application={application} />
      </section>
    )
  }

  return (
    <>
      {step === "download-sample" && (
        <DownloadSampleSection
          application={application}
          header={<Header />}
          onDownloadSample={downloadSample}
          onSampleDownloaded={handleSampleDownloaded}
        />
      )}
      {step === "check-report" && (
        <CheckReportSection
          application={application}
          header={<Header />}
          onReportChecked={reportChecked}
          onPrev={() => setStep("download-sample")}
        />
      )}

      {step === "report-checked" && checkInfo && (
        <>
          {checkInfo.error_count === 0 && checkedFile && application.sample && (
            <ReportValidSection
              header={<Header />}
              fileName={checkInfo.file_name}
              commentCount={checkInfo.comment_count}
              onReportAccepted={onReportAccepted}
              file={checkedFile}
              applicationId={application.sample?.application_id}
              onPrev={() => setStep("check-report")}
            />
          )}
          {checkInfo.error_count > 0 && (
            <ReportErrorsSection
              header={<Header />}
              checkInfo={checkInfo}
              onCheckAgain={() => setStep("check-report")}
            />
          )}
        </>
      )}
    </>
  )
}

export default ApplicationDetailsPending
