import { formatDate } from "common/utils/formatters"
import { Trans } from "react-i18next"
import { DoubleCountingApplicationDetails } from "../types"


export const ApplicationInfo = ({ application }: { application?: DoubleCountingApplicationDetails }) => {
  const productionSite = application?.production_site ?? "N/A"
  const producer = application?.producer.name ?? "N/A"
  const user = application?.producer_user ?? "N/A"
  const creationDate = application?.created_at
    ? formatDate(application.created_at)
    : "N/A"
  return <section>
    <p>
      <Trans
        values={{ producer, productionSite, creationDate, user }}
        defaults="Pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b>, soumis par <b>{{ user }}</b> le <b>{{ creationDate }}</b>"
      />
    </p>
  </section>
}
