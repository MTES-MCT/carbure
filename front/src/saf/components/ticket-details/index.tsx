import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Cross, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useRef } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketStatus } from "saf/types"
import { safTicketDetails } from "saf/__test__/data"
import NavigationButtons from "transaction-details/components/lots/navigation"
import * as api from "../../api"
import TicketTag from "../tickets/tag"
import CancelAssignment from "./cancel-assignment"
import { TicketFields } from "./fields"

export interface TicketDetailsProps {
  neighbors: number[]
}
export const TicketDetails = ({ neighbors }: TicketDetailsProps) => {
  const { t } = useTranslation()
  const commentRef = useRef<HTMLElement>(null)

  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotify()
  const entity = useEntity()
  const match = useHashMatch("ticket/:id")
  const portal = usePortal()

  const ticketResponse = useQuery(api.getSafTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })

  const ticket = ticketResponse.result?.data?.data
  // const ticket = safTicketDetails //TO TEST
  // const commentRef = ticket
  //   ? ticket?.client_comment?.length > 0
  //   : false

  // useEffect(() => { TODO go to comment block
  //   if (hasAssignements && assignementsRef?.current)
  //     assignementsRef.current.scrollIntoView({
  //       block: "end",
  //       behavior: "smooth",
  //     })
  // }, [assignementsRef, hasAssignements])

  const handleTicketCanceled = () => {
    notify(
      t("Le ticket a été annulé et son volume peut être à nouveau affecté."),
      { variant: "success" }
    )
  }

  const showCancelModal = () => {
    //TODO show modal
    portal((close) => (
      <CancelAssignment
        ticket={ticket!}
        onClose={close}
        onTicketCanceled={handleTicketCanceled}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TicketTag status={ticket?.status} />
          <h1>
            {t("Ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <TicketFields ticket={ticket} />
          </section>
          {/* {hasComment && (
            <section ref={assignementsRef}>
              <ClientComment ticketSource={ticketSource} />
            </section>
          )} */}
        </main>

        <footer>
          {ticket?.status === SafTicketStatus.Pending && (
            <Button
              icon={Cross}
              label={t("Annuler l'affectation")}
              variant="danger"
              disabled={!ticket}
              action={showCancelModal}
            />
          )}
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TicketDetails

//TODO Comment from client
// const ClientComment = ({ parent_lot }: { parent_lot?: LotPreview }) => {
//   const { t } = useTranslation()
//   return (
//     <Collapse isOpen={true} variant="info" icon={Split} label={"Lot Initial"}>
//       <section>
//         <ul>
//           <li>
//             {parent_lot ? (
//               <Button variant="link">{parent_lot.carbure_id}</Button>
//             ) : (
//               t("Inconnu")
//             )}
//           </li>
//         </ul>
//       </section>
//       <footer></footer>
//     </Collapse>
//   )
// }
