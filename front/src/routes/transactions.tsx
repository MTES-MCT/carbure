import React, { useState } from "react"

import { Settings } from "../services/settings"

import useAPI, { ApiState } from "../hooks/use-api"
import { getSnapshot, LotStatus } from "../services/lots"
import TransactionSnapshot from "../components/transaction-snapshot"

type TransactionsProps = {
  settings: ApiState<Settings>
  entity: number
}

type ActiveStatus = { [k: string]: boolean }

const Transactions = ({ settings, entity }: TransactionsProps) => {
  const snapshot = useAPI(getSnapshot)

  const [activeStatus, setActiveStatus] = useState<ActiveStatus>({
    [LotStatus.Drafts]: true,
    [LotStatus.ToFix]: false,
    [LotStatus.Accepted]: false,
    [LotStatus.Validated]: false,
  })

  function toggleStatus(status: LotStatus) {
    setActiveStatus({ ...activeStatus, [status]: !activeStatus[status] })
  }

  if (entity < 0 || !settings.data) {
    return null
  }

  const right = settings.data.rights.find(
    (right) => right.entity.id === entity
  )!

  snapshot.useResolve(right.entity.id)

  return (
    <React.Fragment>
      <TransactionSnapshot
        snapshot={snapshot}
        activeStatus={activeStatus}
        toggleStatus={toggleStatus}
      />
    </React.Fragment>
  )
}

export default Transactions
