import { Fragment } from "react"
import { ActionBar } from "common-v2/components/scaffold"
import { LotQuery } from "transactions-v2/types"
import { useStatus } from "transactions-v2/components/status"
import { CreateButton, ExportButton } from "transactions-v2/actions"
import { AcceptManyButton } from "transactions-v2/actions/accept"
import { SendManyButton } from "transactions-v2/actions/send"
import { DeleteManyButton } from "transactions-v2/actions/delete"
import { RejectManyButton } from "transactions-v2/actions/reject"
import { ImportButton } from "transactions-v2/actions/import"
import { RequestManyFixesButton } from "transactions-v2/actions/request-fix"
import { MarkManyAsFixedButton } from "transactions-v2/actions/mark-as-fixed"
import { RecallManyButton } from "transactions-v2/actions/recall"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
}

export const LotActions = ({ count, ...props }: ActionBarProps) => {
  const status = useStatus()
  const empty = count === 0

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
          <AcceptManyButton {...props} disabled={empty} />
          <RejectManyButton {...props} disabled={empty} />
          <RequestManyFixesButton {...props} />
        </Fragment>
      )}

      {status === "out" && (
        <Fragment>
          <RecallManyButton {...props} />
          <MarkManyAsFixedButton {...props} />
        </Fragment>
      )}

      <ExportButton {...props} />
    </ActionBar>
  )
}

export default LotActions
