import { Fragment } from "react"
import { Lot } from "transactions/types"
import { AcceptOneButton } from "transactions/actions/accept"
import { SendOneButton } from "transactions/actions/send"
import { DeleteOneButton } from "transactions/actions/delete"
import { RejectOneButton } from "transactions/actions/reject"
import { RequestOneFixButton } from "transactions/actions/request-fix"
import { MarkOneAsFixedButton } from "transactions/actions/mark-as-fixed"
import useEntity from "carbure/hooks/entity"
import { RecallOneButton } from "transactions/actions/recall"
import { ApproveOneFixButton } from "transactions/actions/approve-fix"

export interface ActionBarProps {
  icon?: boolean
  lot: Lot
}

export const LotActions = ({ lot }: ActionBarProps) => {
  const entity = useEntity()

  const isCreator = lot.added_by?.id === entity.id
  const isSupplier = lot.carbure_supplier?.id === entity.id
  const isClient = lot.carbure_client?.id === entity.id

  const status = lot.lot_status
  const correction = lot.correction_status

  return (
    <Fragment>
      {status === "DRAFT" && <SendOneButton lot={lot} />}

      {(status === "DRAFT" || status === "REJECTED") && (
        <DeleteOneButton lot={lot} />
      )}

      {isClient && status === "PENDING" && correction === "NO_PROBLEMO" && (
        <Fragment>
          <AcceptOneButton lot={lot} />
          <RejectOneButton lot={lot} />
        </Fragment>
      )}

      {(isCreator || isSupplier) && status !== "DRAFT" && (
        <Fragment>
          {correction === "NO_PROBLEMO" && <RecallOneButton lot={lot} />}
          {correction === "IN_CORRECTION" && <MarkOneAsFixedButton lot={lot} />}
        </Fragment>
      )}

      {isClient && !isCreator && !isSupplier && status !== "DRAFT" && (
        <Fragment>
          {correction === "FIXED" && <ApproveOneFixButton lot={lot} />}
          {["NO_PROBLEMO", "FIXED"].includes(correction) && (
            <RequestOneFixButton lot={lot} />
          )}
        </Fragment>
      )}
    </Fragment>
  )
}

export default LotActions
