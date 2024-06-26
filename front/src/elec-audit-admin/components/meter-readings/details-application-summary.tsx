import Form from "common/components/form"
import { TextInput } from "common/components/input"
import { formatDate, formatNumber } from "common/utils/formatters"
import { ElecMeterReadingsApplication } from "elec/types"
import { useTranslation } from "react-i18next"


const ApplicationSummary = ({ application }: { application: ElecMeterReadingsApplication | undefined }) => {
  const { t } = useTranslation()

  return <Form
    id="lot-form"
    variant="columns"
    wrapper
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
      label={t("kWh renouvelables")}
      value={application ? formatNumber(Math.round(application.energy_total)) : "..."}
    />
    <TextInput
      readOnly
      label={t("Points de recharge")}
      value={application ? formatNumber(application.charge_point_count) : "..."}
    />
    <TextInput
      readOnly
      label={t("Part renouvelable de l'électricité sur la période")}
      value={"24,92%"}
    />
  </Form>
}


export default ApplicationSummary
