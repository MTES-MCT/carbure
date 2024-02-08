import { Fragment } from "react"
import { ActionBar } from "common/components/scaffold"
import { LotQuery } from "transactions/types"
import { useStatus } from "transactions/components/status"
import { CreateButton } from "transactions/actions/create"
import { AcceptManyButton } from "transactions/actions/accept"
import { SendManyButton } from "transactions/actions/send"
import { DeleteManyButton } from "transactions/actions/delete"
import { RejectManyButton } from "transactions/actions/reject"
import { ImportButton } from "transactions/actions/import"
import { RequestManyFixesButton } from "transactions/actions/request-fix"
import { MarkManyAsFixedButton } from "transactions/actions/mark-as-fixed"
import { RecallManyButton } from "transactions/actions/recall"
import { ApproveManyFixesButton } from "transactions/actions/approve-fix"
import { ExportLotsButton } from "transactions/actions/export"
import { CancelAcceptManyButton } from "transactions/actions/cancel-accept"

export interface ActionBarProps {
  count: number
  category: string
  query: LotQuery
  selection: number[]
}

export const LotActions = ({ count, category, ...props }: ActionBarProps) => {
  const status = useStatus()
  const empty = count === 0

  return (
    <ActionBar>
      {status === "drafts" && (
        <Fragment>
          <ImportButton />
          <CreateButton />
          <SendManyButton {...props} disabled={empty} />
          <DeleteManyButton all {...props} disabled={empty} />
        </Fragment>
      )}

      {status === "in" && (
        <Fragment>
          {category === "pending" && (
            <Fragment>
              <AcceptManyButton {...props} disabled={empty} />
              <RejectManyButton {...props} disabled={empty} />
            </Fragment>
          )}
          {category === "correction" && <ApproveManyFixesButton {...props} />}
          {category === "history" && <CancelAcceptManyButton {...props} />}
          <RequestManyFixesButton {...props} />
          <DeleteManyButton {...props} />
        </Fragment>
      )}

      {status === "out" && (
        <Fragment>
          {category === "correction" && (
            <Fragment>
              <MarkManyAsFixedButton {...props} />
              <DeleteManyButton {...props} />
            </Fragment>
          )}
          <RecallManyButton {...props} />
        </Fragment>
      )}

      <ExportLotsButton asideX {...props} />
    </ActionBar>
  )
}

export default LotActions
