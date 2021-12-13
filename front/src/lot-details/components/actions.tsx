import { Fragment } from "react"
import { Lot } from "transactions-v2/types"
import { AcceptOneButton } from "transactions-v2/actions/accept"
import { SendOneButton } from "transactions-v2/actions/send"
import { DeleteOneButton } from "transactions-v2/actions/delete"
import { RejectOneButton } from "transactions-v2/actions/reject"
import { RequestOneFixButton } from "transactions-v2/actions/request-fix"
import { MarkOneAsFixedButton } from "transactions-v2/actions/mark-as-fixed"
import useEntity from "carbure/hooks/entity"
import { RecallOneButton } from "transactions-v2/actions/recall"
import { ApproveOneFixButton } from "transactions-v2/actions/approve-fix"

export interface ActionBarProps {
  icon?: boolean
  lot: Lot
}

export const LotActions = ({ lot }: ActionBarProps) => {
  const entity = useEntity()

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

      {status === "PENDING" && correction === "NO_PROBLEMO" && isClient && (
        <Fragment>
          <AcceptOneButton lot={lot} />
          <RejectOneButton lot={lot} />
          <RequestOneFixButton lot={lot} />
        </Fragment>
      )}

      {correction === "FIXED" && <ApproveOneFixButton lot={lot} />}

      {status === "PENDING" && isSupplier && (
        <Fragment>
          {correction === "NO_PROBLEMO" && <RecallOneButton lot={lot} />}
          {correction === "IN_CORRECTION" && <MarkOneAsFixedButton lot={lot} />}
        </Fragment>
      )}
    </Fragment>
  )
}

export default LotActions
