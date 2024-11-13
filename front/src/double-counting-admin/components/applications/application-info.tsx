import { formatDate } from "common/utils/formatters"
import { Trans } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../../../double-counting/types"
import { Link } from "react-router-dom"
import { ROUTE_URLS } from "common/utils/routes"
import useEntity from "carbure/hooks/entity"
import { Fragment } from "react"

export const ApplicationInfo = ({
  application,
}: {
  application?: DoubleCountingApplicationDetails
}) => {
  const productionSite = application?.production_site.name ?? "N/A"
  const producer = application?.producer.name ?? "N/A"
  const user = application?.producer_user ?? "N/A"
  const creationDate = application?.created_at
    ? formatDate(application.created_at)
    : "N/A"
  const entity = useEntity()
  return (
    <section>
      <p>
        <Trans
          values={{ producer, productionSite, creationDate, user }}
          components={{
            Link: application ? (
              <Link
                to={ROUTE_URLS.ADMIN_COMPANY_DETAIL(
                  entity.id,
                  application?.producer.id
                )}
                target="_blank"
              />
            ) : (
              <Fragment />
            ),
          }}
          defaults="Pour le site de production <b>{{ productionSite }}</b> de <b><Link>{{ producer }}</Link></b>, soumis par <b>{{ user }}</b> le <b>{{ creationDate }}</b>"
        />
      </p>
    </section>
  )
}
