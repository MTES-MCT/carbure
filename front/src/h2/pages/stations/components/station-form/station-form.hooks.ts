import { useForm } from "common/components/form2"
import {
  AccessType,
  DistributedPressure,
  H2Station,
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

export function useStationForm(station?: H2Station) {
  return useForm<H2StationFormData>({
    name: station?.name ?? "",
    site_siret: station?.site_siret ?? undefined,
    address: station?.address ?? undefined,
    city: station?.city ?? undefined,
    postal_code: station?.postal_code ?? undefined,
    access_type: station?.access_type ?? AccessType.PUBLIC,
    distributed_pressure: station?.distributed_pressure ?? [],
    has_personal_vehicle_connector:
      station?.has_personal_vehicle_connector ?? false,
    storage_capacity: station?.storage_capacity ?? undefined,
    distribution_capacity: station?.distribution_capacity ?? undefined,
    commissioning_date: station?.commissioning_date ?? undefined,
  })
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
