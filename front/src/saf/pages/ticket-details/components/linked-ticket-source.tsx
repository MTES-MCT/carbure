import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { SafParentTicketSource } from "saf/types"

const LinkedTicketSource = ({
  ticket_source,
  title,
}: {
  ticket_source?: SafParentTicketSource
  title: string
}) => {
  return (
    <Collapse defaultExpanded label={title}>
      <Button
        customPriority="link"
        linkProps={{ href: `#ticket-source/${ticket_source?.id}` }}
      >
        Volume #{ticket_source?.carbure_id}
      </Button>
    </Collapse>
  )
}

export default LinkedTicketSource
