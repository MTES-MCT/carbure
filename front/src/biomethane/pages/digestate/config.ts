import { BiomethaneDigestateInputRequest } from "./types"

export const DIGESTATE_SECTIONS: Record<
  string,
  (keyof BiomethaneDigestateInputRequest)[]
> = {
  production: [
    "raw_digestate_tonnage_produced",
    "raw_digestate_dry_matter_rate",
    "solid_digestate_tonnage",
    "liquid_digestate_quantity",
  ],
  composting: [
    "composting_locations",
    "external_platform_name",
    "external_platform_digestate_volume",
    "external_platform_department",
    "external_platform_municipality",
    "on_site_composted_digestate_volume",
  ],
}
