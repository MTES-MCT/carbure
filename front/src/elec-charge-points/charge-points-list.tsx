import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"
import * as api from "../../api-charge-points"

type ChargePointsListProps = {
  year: number
}

const ChargePointsList = ({ year }: ChargePointsListProps) => {
  const entity = useEntity()
  // const [state, actions] = useCBQueryParamsStore(entity, year)

  // const query = useCBQueryBuilder(state)
  // const applicationsResponse = useQuery(api.getChargePointsList, {
  //   key: "charge-points-list",
  //   params: [query],
  // })

  // const applications = applicationsResponse.result?.data.data ?? []

  return <div>charge points list</div>
}

export default ChargePointsList
