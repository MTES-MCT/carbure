import { formatDate, formatDateYear } from "common/utils/formatters"
import { Trans } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../../../double-counting/types"
import { Link } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"
import useEntity from "common/hooks/entity"
import { Fragment } from "react"
import { useTranslation } from "react-i18next"
export const ApplicationInfo = ({
  application,
}: {
  application?: DoubleCountingApplicationDetails
}) => {
  const productionSite = application?.production_site.name ?? "N/A"
  const producer = application?.producer.name ?? "N/A"
  const user = application?.producer_user ?? "N/A"
  const period = application?.period_start
    ? `${formatDateYear(application.period_start)}-${formatDateYear(application.period_end)}`
    : "N/A"
  const creationDate = application?.created_at
    ? formatDate(application.created_at)
    : "N/A"
  const entity = useEntity()
  const { t } = useTranslation()
  return (
    <section>
      <p>
        <Trans
          values={{ producer, productionSite, creationDate, user, period }}
          components={{
            Link: application ? (
              <Link
                to={
                  ROUTE_URLS.ADMIN(entity.id).COMPANY_DETAIL(
                    application?.producer.id
                  ) + "#double-counting"
                }
                target="_blank"
              />
            ) : (
              <Fragment />
            ),
          }}
          defaults={t(
            "Pour le site de production <b>{{ productionSite }}</b> de <b><Link>{{ producer }}</Link></b>, soumis par <b>{{ user }}</b> le <b>{{ creationDate }}</b>"
          )}
        />
      </p>
      <p>
        <Trans
          values={{ period }}
          defaults="Période de validité : <b>{{ period }}</b>"
        />
      </p>
    </section>
  )
}
