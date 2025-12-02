/**
 * Type safety check for biomethane fields configuration.
 *
 * This file ensures that all fields defined in BIOMETHANE_SECTIONS_CONFIG
 * are present in the corresponding API types (BiomethaneDigestate and BiomethaneEnergy).
 *
 * If any field from the config is missing from the API types, TypeScript will
 * generate a compile-time error listing the missing fields.
 *
 * This prevents runtime errors by catching configuration mismatches at build time.
 */

import { apiTypes } from "common/services/api-fetch.types"
import { BIOMETHANE_SECTIONS_CONFIG } from "./missing-fields.config"

// Extract API types for digestate and energy
type Digestate = apiTypes["BiomethaneDigestate"]
type Energy = apiTypes["BiomethaneEnergy"]

// Exclude metadata fields that are not part of the form configuration
type DigestateExcludedFields = Omit<
  Digestate,
  "producer" | "id" | "year" | "spreadings"
>
type EnergyExcludedFields = Omit<Energy, "producer" | "id" | "year">

// Extract all field names from the configuration
type DigestateEnergyFields =
  (typeof BIOMETHANE_SECTIONS_CONFIG)[keyof typeof BIOMETHANE_SECTIONS_CONFIG][number]

// Find fields that are in the config but not in the API types
// If all fields are covered, MissingFields will be 'never'
type MissingFields = Exclude<
  DigestateEnergyFields,
  keyof DigestateExcludedFields | keyof EnergyExcludedFields
>

/**
 * Type check that validates all configuration fields exist in API types.
 *
 * This will generate a TypeScript error at compile time if:
 * - MissingFields is not 'never' (meaning some fields are missing)
 * - The error message will list all missing fields
 *
 * If all fields are present, this resolves to 'true' and no error is shown.
 */
export const _typeCheck: MissingFields extends never
  ? true
  : `Missing fields: ${MissingFields & string}` = true
