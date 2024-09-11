import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../../api-cpo"

type useElecMeterReadingsSettingsParams = {
  entityId: number
  companyId: number
}
export const useElecMeterReadingsSettings = ({
  entityId,
  companyId,
}: useElecMeterReadingsSettingsParams) => {
  const { t } = useTranslation()
  const applicationsQuery = useQuery(api.getMeterReadingsApplications, {
    key: "meter-readings-applications",
    params: [entityId, companyId],
  })

  const applicationsResponse = applicationsQuery.result?.data.data

  const currentApplicationPeriod =
    applicationsResponse?.current_application_period
  const quarterString = t("T{{quarter}} {{year}}", {
    quarter: currentApplicationPeriod?.quarter,
    year: currentApplicationPeriod?.year,
  })
  const isApplicationsEmpty = applicationsResponse?.applications.length === 0

  return {
    applicationsQuery,
    applications: applicationsResponse?.applications ?? [],
    isApplicationsEmpty,
    chargePointCount: currentApplicationPeriod?.charge_point_count || 0,
    currentApplication: applicationsResponse?.current_application,
    urgencyStatus: currentApplicationPeriod?.urgency_status,
    quarterString,
    currentApplicationPeriod,
  }
}
