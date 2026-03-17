import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { useTranslation } from "react-i18next"
import { SafTicket, SafTicketSource } from "saf/types"

type SafOriginProps = {
  ticket?: SafTicket
  ticketSource?: SafTicketSource
  canAccess?: boolean
}

const SafOrigin = ({ ticket, ticketSource, canAccess }: SafOriginProps) => {
  const { t } = useTranslation()

  const parentLot = ticketSource?.parent_lot
  const parentTicket = ticketSource?.parent_ticket
  const parentTicketSource = ticket?.parent_ticket_source

  if (!canAccess) return null

  return (
    <Collapse label={t("Parent")} defaultExpanded>
      <section>
        <ul>
          {parentLot && (
            <li>
              <Button
                customPriority="link"
                linkProps={{ href: `#lot/${parentLot?.id}` }}
              >
                {`${t("Lot")} #${parentLot.carbure_id}`}
              </Button>
            </li>
          )}
          {parentTicketSource && (
            <li>
              <Button
                customPriority="link"
                linkProps={{ href: `#ticket-source/${parentTicketSource?.id}` }}
              >
                {`${t("Volume")} #${parentTicketSource.carbure_id}`}
              </Button>
            </li>
          )}
          {parentTicket && (
            <li>
              <Button
                customPriority="link"
                linkProps={{ href: `#ticket/${parentTicket?.id}` }}
              >
                {`${t("Ticket")} #${parentTicket.carbure_id}`}
              </Button>
            </li>
          )}
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}

export default SafOrigin
