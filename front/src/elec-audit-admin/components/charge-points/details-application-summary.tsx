import Form from "common/components/form"
import { TextInput } from "common/components/input"
import { formatDate, formatNumber } from "common/utils/formatters"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"




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


export default ApplicationSummary
