import Button from "common/components/button"
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
    <section>
      <Collapse defaultExpanded label={title}>
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
