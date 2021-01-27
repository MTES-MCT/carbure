import { EntitySelection } from "carbure/hooks/use-entity"

import * as api from "transactions/api"
import useAPI from "../../../common/hooks/use-api"

export interface LotDeclarator {
  loading: boolean
  confirmDeclaration: () => Promise<boolean>
}

export default function useDeclareLots(entity: EntitySelection): LotDeclarator {
  const [declaring, declareLots] = useAPI(api.declareLots)

  const loading = declaring.loading

  function confirmDeclaration() {
    return Promise.resolve(true)
  }

  return { loading, confirmDeclaration }
}
