import Collapse from "common/components/collapse"
import { Edit } from "common/components/icons"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { useTranslation } from "react-i18next"
import { SafTicketDetails } from "saf/types"

export interface TicketDetailsProps {
  neighbors: number[]
}

const ClientComment = ({ ticket }: { ticket: SafTicketDetails }) => {
  const { t } = useTranslation()
  const { refToScroll } = useScrollToRef(!!ticket.client_comment)
  if (!ticket.client_comment) return null

  return (
    <section ref={refToScroll}>
      <Collapse
        isOpen={true}
        variant="info"
        icon={Edit}
        label={t("{{client}} a commenté ce ticket :", {
          client: ticket?.client,
        })}
      >
        <section>
          <p>{ticket.client_comment}</p>
        </section>
        <footer></footer>
      </Collapse>
    </section>
  )
}

export default ClientComment
