import { useForm } from "common/components/form2"
import {
  AccessType,
  DistributedPressure,
  H2StationInputRequest,
} from "h2/types"

export type H2StationFormData = {
  name: string | undefined
  site_siret: string | undefined
  address: string | undefined
  city: string | undefined
  postal_code: string | undefined
  access_type: AccessType
  distributed_pressure: DistributedPressure[] | undefined
  has_personal_vehicle_connector: boolean
  storage_capacity: number | undefined
  distribution_capacity: number | undefined
  commissioning_date: string | undefined
}

const defaultStationState: H2StationFormData = {
  name: "",
  site_siret: undefined,
  address: undefined,
  city: undefined,
  postal_code: undefined,
  access_type: AccessType.PUBLIC,
  distributed_pressure: [],
  has_personal_vehicle_connector: false,
  storage_capacity: 0,
  distribution_capacity: 0,
  commissioning_date: undefined,
}

export function useStationForm(initialStationState?: H2StationFormData) {
  return useForm(initialStationState ?? defaultStationState)
}

export function validateStationData(
  data: H2StationFormData
): H2StationInputRequest | undefined {
  if (!data.name) return
  if (!data.site_siret) return
  if (!data.address) return
  if (!data.city) return
  if (!data.postal_code) return
  if (!data.distributed_pressure?.length) return
  if (!data.storage_capacity) return
  if (!data.distribution_capacity) return
  if (!data.commissioning_date) return

  return data as H2StationInputRequest
}
