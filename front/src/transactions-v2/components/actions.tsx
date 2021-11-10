import { Fragment } from "react"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { CreateButton, ExportButton } from "../actions"
import { AcceptButton } from "../actions/accept"
import { SendButton } from "../actions/send"
import { LotQuery } from "../types"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
}

export const Actions = ({ count, ...props }: ActionBarProps) => {
  const status = props.query.status
  const isEmpty = count === 0

  return (
    <ActionBar>
      <ExportButton {...props} />

      {status === "DRAFT" && (
        <Fragment>
          <CreateButton />
          <SendButton {...props} disabled={isEmpty} />
        </Fragment>
      )}

      {status === "IN" && (
        <Fragment>
          <AcceptButton {...props} disabled={isEmpty} />
        </Fragment>
      )}

      {status === "STOCK" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}

      {status === "OUT" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}
    </ActionBar>
  )
}
