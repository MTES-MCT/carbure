import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { Split } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketDetails, SafTicketSourcePreview } from "saf/types"

const LinkedTicketSource = ({
  ticket_source,
  title,
}: {
  ticket_source?: SafTicketSourcePreview
  title: string
}) => {
  const location = useLocation()
  const navigate = useNavigate()

  const showTicketSourceDetails = () => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `ticket-source/${ticket_source?.id}`,
    })
  }

  return (
    <section>
      <Collapse isOpen={true} variant="info" icon={Split} label={title}>
        <section>
          <Button variant="link" action={showTicketSourceDetails}>
            Volume #{ticket_source?.carbure_id}
          </Button>
        </section>
        <footer></footer>
      </Collapse>
    </section>
  )
}

export default LinkedTicketSource
