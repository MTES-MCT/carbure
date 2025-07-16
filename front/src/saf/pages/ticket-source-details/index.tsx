import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import { TicketAssignment } from "saf/components/assignment/simple-assignment"
import { TicketSourceParent } from "./components/ticket-source-parent"
import TicketSourceTag from "../../components/ticket-source-tag"
import AssignedTickets from "./components/assigned-tickets"
import TicketSourceFields from "./components/fields"
import {
  NavigationButtons,
  NavigationButtonsProps,
} from "common/components/navigation"

export type TicketSourceDetailsProps = Partial<
  Omit<NavigationButtonsProps, "closeAction">
>

export const TicketSourceDetails = ({
  limit,
  total,
  fetchIdsForPage,
  baseIdsList,
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
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const ticketSource = ticketSourceResponse.result?.data

  const isOwner = ticketSource?.added_by.id === entity.id

  const assignedVolume = ticketSource?.assigned_volume ?? 0
  const totalVolume = ticketSource?.total_volume ?? 0
  const hasRemainingVolume = assignedVolume < totalVolume

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
      <Dialog
        onClose={closeDialog}
        header={
          <Dialog.Title>
            <TicketSourceTag ticketSource={ticketSource} />
            <span>
              {t("Volume CAD n°")}
              {ticketSource?.carbure_id ?? "..."}
            </span>
            -<span>{ticketSource?.added_by.name}</span>
          </Dialog.Title>
        }
        footer={
          <>
            {baseIdsList && baseIdsList.length > 0 && fetchIdsForPage && (
              <NavigationButtons
                limit={limit}
                total={total ?? 0}
                fetchIdsForPage={fetchIdsForPage}
                baseIdsList={baseIdsList}
              />
            )}
            {isOwner && hasRemainingVolume && (
              <Button
                iconId="ri-send-plane-line"
                priority="primary"
                onClick={showAssignement}
              >
                {t("Affecter")}
              </Button>
            )}
          </>
        }
      >
        <section>
          <TicketSourceFields ticketSource={ticketSource} />
        </section>

        <section>
          <TicketSourceParent ticketSource={ticketSource} />
        </section>

        {hasAssignements && (
          <section ref={refToScroll}>
            <AssignedTickets ticketSource={ticketSource} />
          </section>
        )}

        {ticketSourceResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TicketSourceDetails
