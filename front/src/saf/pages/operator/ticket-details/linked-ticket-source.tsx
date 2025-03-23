import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketSourcePreview } from "saf/pages/operator/types"

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
    <Collapse defaultExpanded label={title}>
      <Button customPriority="link" onClick={showTicketSourceDetails}>
        Volume #{ticket_source?.carbure_id}
      </Button>
    </Collapse>
  )
}

export default LinkedTicketSource
