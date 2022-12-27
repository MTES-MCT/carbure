import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketSourceSummaryItem } from "saf/types"

const ChildTicketSource = ({
  child_ticket_source,
}: {
  child_ticket_source?: SafTicketSourceSummaryItem
}) => {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()

  const showTicketSourceDetails = () => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `ticket-sources/${child_ticket_source?.id}`,
    })
  }

  return (
    <section>
      <Collapse
        isOpen={true}
        variant="info"
        icon={Split}
        label={t("Volume enfant")}
      >
        <section>
          <Button variant="link" action={showTicketSourceDetails}>
            Volume #{child_ticket_source?.carbure_id}
            {/* {t( //TODO adapté en fonciton des types qu'on affichera
              `Volume ${child_ticket_source?.carbure_id} - {{totalVolume}} L - reçu en {{deliveryPeriod}}`,
              {
                totalVolume: child_ticket_source?.total_volume,
                deliveryPeriod: formatPeriod(
                  child_ticket_source?.delivery_period!
                ),
              }
            )} */}
          </Button>
        </section>
        <footer></footer>
      </Collapse>
    </section>
  )
}

export default ChildTicketSource
