import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Send } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import NavigationButtons from "transaction-details/components/lots/navigation"
import * as api from "../../api"
import TicketSourceTag from "../ticket-sources/tag"
import AssignedTickets from "./assigned-tickets"
import TicketAssignment from "../assignment/simple-assignment"
import TicketSourceFields from "./fields"
import ParentLot from "../parent-lot"

export interface TicketSourceDetailsProps {
  neighbors?: number[]
}

export const TicketSourceDetails = ({
  neighbors,
}: TicketSourceDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotify()
  const entity = useEntity()
  const match = useHashMatch("ticket-source/:id")
  const portal = usePortal()

  const ticketSourceResponse = useQuery(api.getOperatorTicketSourceDetails, {
    key: "ticket-source-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const ticketSource = ticketSourceResponse.result?.data?.data
  // const ticketSource = safTicketSourceDetails //TO TEST

  const hasAssignements = ticketSource
    ? ticketSource?.assigned_tickets?.length > 0
    : false

  const { refToScroll } = useScrollToRef(hasAssignements)

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const handleTicketAssigned = (volume: number, clientName: string) => {
    notify(
      t("{{volume}} litres ont bien été affectés à {{clientName}}.", {
        volume,
        clientName,
      }),
      { variant: "success" }
    )
  }

  const showAssignement = () => {
    portal((close) => (
      <TicketAssignment
        ticketSource={ticketSource!}
        onClose={close}
        onTicketAssigned={handleTicketAssigned}
      />
    ))
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TicketSourceTag big ticketSource={ticketSource} />
          <h1>
            {t("Volume CAD n°")}
            {ticketSource?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <TicketSourceFields ticketSource={ticketSource} />
          </section>
          {hasAssignements && (
            <section ref={refToScroll}>
              <AssignedTickets ticketSource={ticketSource} />
            </section>
          )}
          <section>
            <ParentLot parent_lot={ticketSource?.parent_lot} />
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Affecter")}
            variant="primary"
            disabled={
              !ticketSource ||
              ticketSource.assigned_volume === ticketSource.total_volume
            }
            action={showAssignement}
          />
          {neighbors && (
            <NavigationButtons
              neighbors={neighbors}
              closeAction={closeDialog}
            />
          )}
        </footer>

        {ticketSourceResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TicketSourceDetails
