import { Fragment } from "react"
import { Lot } from "transactions-v2/types"
import { AcceptOneButton } from "transactions-v2/actions/accept"
import { SendOneButton } from "transactions-v2/actions/send"
import { DeleteOneButton } from "transactions-v2/actions/delete"
import { RejectOneButton } from "transactions-v2/actions/reject"

export interface ActionBarProps {
  icon?: boolean
  lot: Lot
}

export const LotActions = (props: ActionBarProps) => {
  const status = props.lot.lot_status

  return (
    <Fragment>
      {status === "DRAFT" && (
        <Fragment>
          <SendOneButton {...props} />
          <DeleteOneButton {...props} />
        </Fragment>
      )}

      {status === "PENDING" && (
        <Fragment>
          <AcceptOneButton {...props} />
          <RejectOneButton {...props} />
        </Fragment>
      )}
    </Fragment>
  )
}

export default LotActions
