/**
 * Configuration file for biomethane fields validation system.
 *
 * This file defines the mapping between form sections and their fields
 * for the biomethane annual declaration process. It serves as the central configuration
 * for identifying which sections contain missing mandatory fields and need user attention.
 *
 * The configuration is organized by pages (Digestate and Energy) and their respective
 * sections, with each section containing an array of fields.
 *
 * Key features:
 * - Maps form sections to their fields
 * - Supports dynamic section highlighting and field focusing
 * - Used by the missing fields validation system to guide users to incomplete sections
 *
 * Usage:
 * - The getMissingFieldsSectionIds function uses this config to determine which sections
 *   have missing fields based on the server response
 * - Sections with missing fields are automatically registered and highlighted
 * - Users are guided to incomplete sections with visual indicators and auto-focus
 */

export const DIGESTATE_SECTIONS_CONFIG = {
  // Page Digestat
  production: [
    "raw_digestate_tonnage_produced",
    "raw_digestate_dry_matter_rate",
    "solid_digestate_tonnage",
    "liquid_digestate_quantity",
  ],
  "spreading-distance": ["average_spreading_valorization_distance"],
  composting: [
    "external_platform_name",
    "external_platform_department",
    "external_platform_municipality",
    "on_site_composted_digestate_volume",
    "external_platform_digestate_volume",
    "composting_locations",
  ],
  "incineration-landfill": [
    "annual_eliminated_volume",
    "incinerator_landfill_center_name",
    "wwtp_materials_to_incineration",
  ],
  sale: ["acquiring_companies", "sold_volume"],
} as const

export const ENERGY_SECTIONS_CONFIG = {
  // Page Énergie
  "injected-biomethane": [
    "injected_biomethane_gwh_pcs_per_year",
    "injected_biomethane_nm3_per_year",
    "injected_biomethane_ch4_rate_percent",
    "injected_biomethane_pcs_kwh_per_nm3",
    "operating_hours",
  ],
  "biogas-production": [
    "produced_biogas_nm3_per_year",
    "flared_biogas_nm3_per_year",
    "flaring_operating_hours",
  ],
  "installation-energy-needs": [
    "attest_no_fossil_for_digester_heating_and_purification",
    "energy_used_for_digester_heating",
    "fossil_details_for_digester_heating",
    "attest_no_fossil_for_installation_needs",
    "energy_used_for_installation_needs",
    "fossil_details_for_installation_needs",
  ],
  "energy-efficiency": [
    "purified_biogas_quantity_nm3",
    "purification_electric_consumption_kwe",
    "self_consumed_biogas_nm3",
    "total_unit_electric_consumption_kwe",
    "butane_or_propane_addition",
    "fossil_fuel_consumed_kwh",
  ],
  miscellaneous: [
    "has_opposition_or_complaints_acceptability",
    "estimated_work_days_acceptability",
  ],
  malfunction: [
    "has_malfunctions",
    "malfunction_cumulative_duration_days",
    "malfunction_types",
    "malfunction_details",
    "has_injection_difficulties_due_to_network_saturation",
    "injection_impossibility_hours",
  ],
} as const

export const BIOMETHANE_SECTIONS_CONFIG = {
  ...DIGESTATE_SECTIONS_CONFIG,
  ...ENERGY_SECTIONS_CONFIG,
} as const

export type BiomethaneSectionId = keyof typeof BIOMETHANE_SECTIONS_CONFIG

export const getMissingFieldsSectionIds = (missingFields: string[]) => {
  const missingFieldsSet = new Set(missingFields)
  const config = Object.entries(BIOMETHANE_SECTIONS_CONFIG).filter(
    ([, fields]) => fields.some((field) => missingFieldsSet.has(field))
  )
  return config.map(([sectionId]) => sectionId)
}
