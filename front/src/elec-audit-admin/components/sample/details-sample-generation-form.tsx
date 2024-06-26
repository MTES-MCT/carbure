import { AxiosResponse } from "axios"
import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import Form from "common/components/form"
import { Download } from "common/components/icons"
import { NumberInput } from "common/components/input"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { Api } from "common/services/api"
import { ElecApplicationSample } from "elec-audit-admin/types"
import { useState } from "react"
import { useTranslation } from "react-i18next"

interface SampleGenerationFormProps {
  power_total: number
  applicationId: number | undefined
  generateSampleQuery: (entityId: number, applicationId: number, percentage: number) => Promise<AxiosResponse<Api<ElecApplicationSample>, any>>
  onSampleGenerated: (sample: ElecApplicationSample) => void
  retry?: boolean
}
const SampleGenerationForm = ({
  power_total,
  applicationId,
  retry,
  generateSampleQuery,
  onSampleGenerated
}: SampleGenerationFormProps) => {
  const { t } = useTranslation()
  const [percent, setPercent] = useState<number | undefined>(10)
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const generateSampleMutation = useMutation(generateSampleQuery, {
    onSuccess(response) {
      const sample = response.data.data
      if (!sample) {
        notify(t("L'échantillon n'a pas pu être généré !"), { variant: "warning" })
        return
      }
      onSampleGenerated(sample)
    },
    onError(err) {
      notifyError(err, t("Une erreur est survene, l'échantillon n'a pas pu être généré."))
    },
  })


  const generateSample = () => {
    generateSampleMutation.execute(entity.id, applicationId!, percent!)
  }

  const buttonText = !retry ? t("Générer l'échantillon") : t("Générer un nouvel échantillon")

  return <>
    <strong>{t("Génération de l'échantillon à auditer")}</strong>
    <Form id="generate-sample" onSubmit={generateSample}>

      <NumberInput
        value={percent}
        autoFocus
        onChange={setPercent}
        required
        max={100}
        min={1}
        label={t("Pourcentage de puissance installée à auditeur (%)")}
        icon={() => (
          <Button
            variant={!retry ? "primary" : "secondary"}
            loading={generateSampleMutation.loading}
            icon={Download}
            disabled={!percent || !applicationId}
            label={buttonText}
            submit="generate-sample"
          />
        )}
      />

      <p>{t(`(Soit ${power_total * (percent ?? 0) / 100} kW)`, {})}</p>

    </Form>
  </>
}

export default SampleGenerationForm