import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import { Bar } from "common/components/scaffold"
import { useQueryParamsStore } from "saf/hooks/query-params-store"
import {
  SafFilter,
  SafOperatorSnapshot,
  SafTicketSourceStatus,
} from "saf/types"
import * as api from "../../api"
import { useAutoStatus } from "../operator-tabs"
import { Filters } from "./filters"

export interface CertificatesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: CertificatesProps) => {
  console.log("snapshot:", snapshot)
  // const matomo = useMatomo()
  const location = useLocation()

  const entity = useEntity()
  const status = SafTicketSourceStatus.Available // useAutoStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot) // prettier-ignore

  return (
    <>
      <Bar>
        <Filters
          filters={FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={(filter) => api.getTicketSourceFilters(filter)}
        />
      </Bar>
    </>
  )
}

const FILTERS = [SafFilter.Clients, SafFilter.Feedstocks, SafFilter.Periods]

export default TicketSources
