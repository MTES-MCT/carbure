import { Fragment } from "react"
import { LotQuery } from "../hooks/lot-query"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { CreateButton, ExportButton } from "../actions"
import { AcceptButton } from "../actions/accept"
import { SendManyButton } from "../actions/send"
import { Cross, Wrench } from "common-v2/components/icons"
import useStatus from "transactions-v2/hooks/status"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
}

export const LotActions = ({ count, ...props }: ActionBarProps) => {
  const status = useStatus()
  const { selection } = props

  return (
    <ActionBar>
      {status === "drafts" && (
        <Fragment>
          <CreateButton />
          <SendManyButton {...props} disabled={count === 0} />
          <Button
            disabled={count === 0}
            variant="danger"
            icon={Cross}
            label={
              selection.length > 0 ? "Supprimer sélection" : "Supprimer tout"
            }
          />
        </Fragment>
      )}

      {status === "in" && (
        <Fragment>
          <AcceptButton {...props} disabled={count === 0} />
          <Button
            disabled={count === 0}
            variant="danger"
            icon={Cross}
            label={selection.length > 0 ? "Refuser sélection" : "Refuser tout"}
          />
          <Button
            disabled={count === 0 || selection.length === 0}
            variant="warning"
            icon={Wrench}
            label={"Demander correction"}
          />
        </Fragment>
      )}

      {status === "out" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}

      <ExportButton {...props} />
    </ActionBar>
  )
}

export default LotActions
