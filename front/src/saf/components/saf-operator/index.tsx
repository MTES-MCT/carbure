import { useLocation } from "react-router-dom"

import useEntity from "carbure/hooks/entity"

import { useQueryParamsStore } from "saf/hooks/query-params-store"
import {
  SafOperatorSnapshot
} from "saf/types"
import { useAutoStatus } from "../status"

export interface CertificatesProps {
  year: number
  snapshot: SafOperatorSnapshot | undefined
}

export const TicketSources = ({ year, snapshot }: CertificatesProps) => {
  console.log("snapshot:", snapshot)
  // const matomo = useMatomo()
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot) // prettier-ignore
  return null

}

export default TicketSources
