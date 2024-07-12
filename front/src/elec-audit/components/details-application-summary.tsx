import Form from "common/components/form"
import { TextInput } from "common/components/input"
import { formatDate, formatNumber } from "common/utils/formatters"
import { getApplicationAuditLimitDate } from "elec-audit/helpers"
import { ElecAuditApplicationDetails } from "elec-audit/types"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"




const ApplicationSummary = ({ application }: { application: ElecAuditApplicationDetails | undefined }) => {
  const { t } = useTranslation()
  let limitDate = application?.audit_order_date ? getApplicationAuditLimitDate(application.audit_order_date) : "..."

  return <Form
    variant="columns"
  >

    <TextInput
      readOnly
      label={t("Aménageur")}
      value={application?.cpo.name || "..."}
    />


    <TextInput
      readOnly
      label={t("Ordre de contrôle")}
      value={application ? formatDate(application.audit_order_date!) : "..."}
    />

    <TextInput
      readOnly
      label={t("Date limite de contrôle")}
      value={application ? formatDate(limitDate) : "..."}
    />

    <TextInput
      readOnly
      label={t("Stations")}
      value={application ? formatNumber(application.station_count) : "..."} />

    <TextInput
      readOnly
      label={t("Points de recharge")}
      value={application ? formatNumber(application.charge_point_count) : "..."}
    />


  </Form>
}


export default ApplicationSummary
