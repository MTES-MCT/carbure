import { Fragment } from "react"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { Wrench } from "common-v2/components/icons"
import { LotQuery } from "transactions-v2/types"
import { useStatus } from "transactions-v2/components/status"
import { CreateButton, ExportButton } from "transactions-v2/actions"
import { AcceptManyButton } from "transactions-v2/actions/accept"
import { SendManyButton } from "transactions-v2/actions/send"
import { DeleteManyButton } from "transactions-v2/actions/delete"
import { RejectManyButton } from "transactions-v2/actions/reject"
import { ImportButton } from "transactions-v2/actions/import"
import { RequestFixManyButton } from "transactions-v2/actions/request-fix"
import { MarkAsFixedManyButton } from "transactions-v2/actions/mark-as-fixed"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
}

export const LotActions = ({ count, ...props }: ActionBarProps) => {
  const status = useStatus()
  const { selection } = props
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
          <RequestFixManyButton {...props} disabled={empty} />
        </Fragment>
      )}

      {status === "out" && (
        <Fragment>
          <Button
            disabled={empty || selection.length === 0}
            variant="warning"
            icon={Wrench}
            label={"Corriger la sélection"}
          />
          <MarkAsFixedManyButton {...props} />
        </Fragment>
      )}

      <ExportButton {...props} />
    </ActionBar>
  )
}

export default LotActions
