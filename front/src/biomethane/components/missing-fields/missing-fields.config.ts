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

export const BIOMETHANE_SECTIONS_CONFIG = {
  // Digestate page
  production: [
    { name: "raw_digestate_tonnage_produced", type: "field" },
    { name: "raw_digestate_dry_matter_rate", type: "field" },
    { name: "solid_digestate_tonnage", type: "field" },
    { name: "liquid_digestate_quantity", type: "field" },
  ],
  "spreading-distance": [
    { name: "average_spreading_valorization_distance", type: "field" },
  ],
  spreading: [{ name: "digestate_spreading", type: "section" }],
  composting: [
    { name: "external_platform_name", type: "field" },
    { name: "external_platform_department", type: "field" },
    { name: "external_platform_municipality", type: "field" },
    { name: "on_site_composted_digestate_volume", type: "field" },
    { name: "external_platform_digestate_volume", type: "field" },
    { name: "composting_locations", type: "field" },
  ],
  "incineration-landfill": [
    { name: "annual_eliminated_volume", type: "field" },
    { name: "incinerator_landfill_center_name", type: "field" },
    { name: "wwtp_materials_to_incineration", type: "field" },
  ],
  sale: [
    { name: "acquiring_companies", type: "field" },
    { name: "sold_volume", type: "field" },
  ],

  // Energy page
  "injected-biomethane": [
    { name: "injected_biomethane_gwh_pcs_per_year", type: "field" },
    { name: "injected_biomethane_ch4_rate_percent", type: "field" },
    { name: "injected_biomethane_pcs_kwh_per_nm3", type: "field" },
  ],
  "biogas-production": [
    { name: "produced_biogas_nm3_per_year", type: "field" },
    { name: "flared_biogas_nm3_per_year", type: "field" },
    { name: "flaring_operating_hours", type: "field" },
  ],
  "installation-energy-needs": [
    { name: "attest_no_fossil_for_energy", type: "field" },
    { name: "energy_types", type: "field" },
    { name: "energy_details", type: "field" },
  ],
  "energy-efficiency": [
    { name: "purified_biogas_quantity_nm3", type: "field" },
    { name: "purification_electric_consumption_kwe", type: "field" },
    { name: "self_consumed_biogas_nm3", type: "field" },
    { name: "self_consumed_biogas_or_biomethane_kwh", type: "field" },
    { name: "total_unit_electric_consumption_kwe", type: "field" },
    { name: "butane_or_propane_addition", type: "field" },
    { name: "fossil_fuel_consumed_kwh", type: "field" },
  ],
  "monthly-biomethane-injection": [
    { name: "energy_monthly_report", type: "section" },
  ],
  acceptability: [
    { name: "has_opposition_or_complaints_acceptability", type: "field" },
    { name: "estimated_work_days_acceptability", type: "field" },
  ],
  malfunction: [
    { name: "has_malfunctions", type: "field" },
    { name: "malfunction_cumulative_duration_days", type: "field" },
    { name: "malfunction_types", type: "field" },
    { name: "malfunction_details", type: "field" },
    {
      name: "has_injection_difficulties_due_to_network_saturation",
      type: "field",
    },
    { name: "injection_impossibility_hours", type: "field" },
  ],

  // Contract page
  "contract-infos": [
    { name: "tariff_reference", type: "field" },
    { name: "buyer", type: "field" },
    { name: "installation_category", type: "field" },
    { name: "cmax", type: "field" },
    { name: "pap_contracted", type: "field" },
    { name: "cmax_annualized", type: "field" },
    { name: "cmax_annualized_value", type: "field" },
  ],
  "contract-files": [
    { name: "conditions_file", type: "section" },
    { name: "effective_date", type: "section" },
    { name: "signature_date", type: "section" },
  ],
  "contract-aid-organism": [
    {
      name: "has_complementary_investment_aid",
      type: "field",
    },
    { name: "complementary_aid_organisms", type: "field" },
  ],

  // Production page (unité de production)
  "general-info": [
    { name: "name", type: "field" },
    { name: "site_siret", type: "field" },
    { name: "unit_type", type: "field" },
    { name: "address", type: "field" },
    { name: "postal_code", type: "field" },
    { name: "city", type: "field" },
    { name: "department", type: "field" },
    { name: "insee_code", type: "field" },
  ],
  "sanitary-agreement": [
    { name: "has_sanitary_approval", type: "field" },
    { name: "sanitary_approval_number", type: "field" },
    { name: "has_hygienization_exemption", type: "field" },
    { name: "hygienization_exemption_type", type: "field" },
  ],
  icpe: [
    { name: "icpe_number", type: "field" },
    { name: "icpe_regime", type: "field" },
  ],
  "production-site": [
    { name: "process_type", type: "field" },
    { name: "methanization_process", type: "field" },
    { name: "production_efficiency", type: "field" },
    { name: "installed_meters", type: "field" },
    { name: "has_hygienization_unit", type: "field" },
    { name: "has_co2_valorization_process", type: "field" },
  ],
  "digestate-processing": [
    { name: "has_digestate_phase_separation", type: "field" },
    { name: "raw_digestate_treatment_steps", type: "field" },
    { name: "liquid_phase_treatment_steps", type: "field" },
    { name: "solid_phase_treatment_steps", type: "field" },
    { name: "digestate_valorization_methods", type: "field" },
    { name: "spreading_management_methods", type: "field" },
    { name: "digestate_sale_types", type: "field" },
  ],
  "digestate-storage": [{ name: "digestate_storage", type: "section" }],
} as const

// Index built once at module loading
const FIELD_TO_SECTION_INDEX: Record<string, FieldToSectionEntry> =
  Object.entries(BIOMETHANE_SECTIONS_CONFIG).reduce(
    (acc, [sectionId, fields]) => {
      for (const field of fields) {
        acc[field.name] = {
          sectionId: sectionId as BiomethaneSectionId,
          field,
        }
      }
      return acc
    },
    {} as Record<string, FieldToSectionEntry>
  )

export type BiomethaneSectionId = keyof typeof BIOMETHANE_SECTIONS_CONFIG
type BiomethaneFieldConfig =
  (typeof BIOMETHANE_SECTIONS_CONFIG)[BiomethaneSectionId][number]
type FieldToSectionEntry = {
  sectionId: BiomethaneSectionId
  field: BiomethaneFieldConfig
}

export const getMissingFieldsSectionIds = (missingFields: string[]) => {
  const missingFieldsSet = new Set(missingFields)
  const config = Object.entries(BIOMETHANE_SECTIONS_CONFIG).filter(
    ([, fields]) => fields.some((field) => missingFieldsSet.has(field.name))
  )
  return config.map(([sectionId]) => sectionId)
}

export const getMissingFieldConfig = (
  missingField: string
): FieldToSectionEntry | null => {
  return FIELD_TO_SECTION_INDEX[missingField] ?? null
}

/** Returns the list of field names (config keys) for a given section. */
export const getFieldNamesForSection = (
  sectionId: BiomethaneSectionId
): string[] => {
  const fields = BIOMETHANE_SECTIONS_CONFIG[sectionId]
  return fields ? fields.map((f) => f.name) : []
}
