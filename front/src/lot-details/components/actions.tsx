import { Fragment } from "react"
import { Lot } from "transactions-v2/types"
import { AcceptOneButton } from "transactions-v2/actions/accept"
import { SendOneButton } from "transactions-v2/actions/send"
import { DeleteOneButton } from "transactions-v2/actions/delete"
import { RejectOneButton } from "transactions-v2/actions/reject"
import { RequestFixOneButton } from "transactions-v2/actions/request-fix"
import { MarkAsFixedOneButton } from "transactions-v2/actions/mark-as-fixed"
import useEntity from "carbure/hooks/entity"

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
      {status === "DRAFT" && (
        <Fragment>
          <SendOneButton lot={lot} />
          <DeleteOneButton lot={lot} />
        </Fragment>
      )}

      {status === "PENDING" && isClient && (
        <Fragment>
          <AcceptOneButton lot={lot} />
          <RejectOneButton lot={lot} />
          <RequestFixOneButton lot={lot} />
        </Fragment>
      )}

      {status === "PENDING" && isSupplier && (
        <Fragment>
          {/* {correction === "NO_PROBLEMO" && <MarkAsFixedOneButton lot={lot} />} */}
          {correction === "IN_CORRECTION" && <MarkAsFixedOneButton lot={lot} />}
        </Fragment>
      )}
    </Fragment>
  )
}

export default LotActions
