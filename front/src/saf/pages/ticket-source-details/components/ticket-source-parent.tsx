import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { useTranslation } from "react-i18next"
import { SafTicketSource } from "saf/types"

export const TicketSourceParent = ({
  ticketSource,
}: {
  ticketSource?: SafTicketSource
}) => {
  const { t } = useTranslation()

  const parentLot = ticketSource?.parent_lot
  const parentTicket = ticketSource?.parent_ticket

  return (
    <Collapse label={t("Parent")} defaultExpanded>
      <section>
        <ul>
          <li>
            {parentLot && (
              <Button
                customPriority="link"
                linkProps={{ href: `#lot/${parentLot?.id}` }}
              >
                {`${t("Lot")} #${parentLot.carbure_id}`}
              </Button>
            )}
            {parentTicket && (
              <Button
                customPriority="link"
                linkProps={{ href: `#ticket/${parentTicket?.id}` }}
              >
                {`${t("Ticket")} #${parentTicket.carbure_id}`}
              </Button>
            )}
          </li>
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}
