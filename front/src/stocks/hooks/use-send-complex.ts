import { useEffect } from "react"
import { useParams } from "react-router-dom"

import { LotStatus } from "common/types"
import { EntitySelection } from "carbure/hooks/use-entity"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"
import * as api from "stocks/api"

export default function useSendStockComplex(
  entity: EntitySelection,
) {
  const close = useClose("../")
  const entityID = entity?.id
  const [request, resolve] = useAPI(api.sendStockComplex)

  return {
    request,
    close,
  }
}
