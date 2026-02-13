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

  const originLot = ticketSource?.origin_lot ?? ticket?.origin_lot
  const parentLot = ticketSource?.parent_lot
  const parentTicket = ticketSource?.parent_ticket
  const parentTicketSource = ticket?.parent_ticket_source

  return (
    <Collapse label={t("Origine")} defaultExpanded>
      <section>
        <ul>
          {originLot && originLot?.id !== parentLot?.id && (
            <li>{<p>{`${t("POS")} #${originLot.carbure_id}`}</p>}</li>
          )}
          {canAccess && parentLot && (
            <li>
              <Button
                customPriority="link"
                linkProps={{ href: `#lot/${parentLot?.id}` }}
              >
                {`${t("Lot")} #${parentLot.carbure_id}`}
              </Button>
            </li>
          )}
          {canAccess && parentTicketSource && (
            <li>
              <Button
                customPriority="link"
                linkProps={{ href: `#ticket-source/${parentTicketSource?.id}` }}
              >
                {`${t("Volume")} #${parentTicketSource.carbure_id}`}
              </Button>
            </li>
          )}
          {canAccess && parentTicket && (
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
