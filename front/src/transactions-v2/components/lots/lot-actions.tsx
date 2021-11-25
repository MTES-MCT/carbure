import { Fragment } from "react"
import { LotQuery } from "../../types"
import { useStatus } from "../status"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { Cross, Wrench } from "common-v2/components/icons"
import { CreateButton, ExportButton } from "../../actions"
import { AcceptButton } from "../../actions/accept"
import { SendManyButton } from "../../actions/send"
import { DeleteManyButton } from "../../actions/delete"

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
          <SendManyButton {...props} disabled={empty} />
          <DeleteManyButton {...props} disabled={empty} />
        </Fragment>
      )}

      {status === "in" && (
        <Fragment>
          <AcceptButton {...props} disabled={empty} />
          <Button
            disabled={empty}
            variant="danger"
            icon={Cross}
            label={
              selection.length > 0 ? "Refuser la sélection" : "Refuser tout"
            }
          />
          <Button
            disabled={empty || selection.length === 0}
            variant="warning"
            icon={Wrench}
            label={"Demander une correction"}
          />
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
        </Fragment>
      )}

      <ExportButton {...props} />
    </ActionBar>
  )
}

export default LotActions
