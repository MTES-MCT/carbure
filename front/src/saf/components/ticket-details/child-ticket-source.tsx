import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketDetails } from "saf/types"

const ChildTicketSource = ({
  child_ticket_source,
}: {
  child_ticket_source?: SafTicketDetails["child_ticket_source"]
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
          </Button>
        </section>
        <footer></footer>
      </Collapse>
    </section>
  )
}

export default ChildTicketSource
