import { Fragment } from "react"
import { ActionBar } from "common-v2/components/scaffold"
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

export interface ActionBarProps {
  count: number
  category: string
  query: LotQuery
  selection: number[]
}

export const LotActions = ({ count, category, ...props }: ActionBarProps) => {
  const status = useStatus()
  const empty = count === 0
  const noSelection = props.selection.length === 0

  return (
    <ActionBar>
      {status === "drafts" && (
        <Fragment>
          <CreateButton />
          <ImportButton />
          <SendManyButton {...props} disabled={empty} />
          <DeleteManyButton {...props} disabled={empty} />
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
          {category !== "correction" && <RequestManyFixesButton {...props} />}
          {category === "correction" && <ApproveManyFixesButton {...props} />}
        </Fragment>
      )}

      {status === "out" && (
        <Fragment>
          {category !== "correction" && <RecallManyButton {...props} />}
          {category === "correction" && (
            <Fragment>
              <MarkManyAsFixedButton {...props} />
              <DeleteManyButton {...props} disabled={noSelection} />
            </Fragment>
          )}
        </Fragment>
      )}

      <ExportLotsButton {...props} />
    </ActionBar>
  )
}

export default LotActions
