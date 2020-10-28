import { EntitySelection } from "../helpers/use-entity"
import { TransactionSelection } from "../query/use-selection"
import { YearSelection } from "../query/use-year"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

import { confirm, prompt } from "../../components/system/dialog"

export interface LotAcceptor {
  loading: boolean
  acceptLot: (l: number) => void
  acceptAndCommentLot: (l: number) => void
  acceptSelection: () => void
  acceptAllInbox: () => void
}

export default function useAcceptLots(
  entity: EntitySelection,
  selection: TransactionSelection,
  year: YearSelection,
  refresh: () => void
): LotAcceptor {
  const [request, resolveAccept] = useAPI(api.acceptLots)
  const [requestAll, resolveAcceptAll] = useAPI(api.acceptAllInboxLots)

  async function acceptLot(lotID: number) {
    const shouldAccept = await confirm(
      "Accepter lots",
      "Voulez vous accepter ce lot ?"
    )

    if (entity !== null && shouldAccept) {
      resolveAccept(entity.id, [lotID]).then(refresh)
    }
  }

  async function acceptAndCommentLot(lotID: number) {
    const comment = await prompt(
      "Accepter lots",
      "Voulez vous accepter ce lot sous réserve ?"
    )

    if (entity !== null && comment) {
      resolveAccept(entity.id, [lotID]).then(refresh)
    }
  }

  async function acceptSelection() {
    const shouldAccept = await confirm(
      "Accepter lots",
      "Voulez vous accepter les lots sélectionnés ?"
    )

    if (entity !== null && shouldAccept) {
      resolveAccept(entity.id, selection.selected).then(refresh)
    }
  }

  async function acceptAllInbox() {
    const shouldAccept = await confirm(
      "Accepter lots",
      "Voulez vous accepter tous ces lots ?"
    )

    if (entity !== null && shouldAccept) {
      resolveAcceptAll(entity.id, year.selected).then(refresh)
    }
  }

  return {
    loading: request.loading || requestAll.loading,
    acceptLot,
    acceptAndCommentLot,
    acceptSelection,
    acceptAllInbox,
  }
}
