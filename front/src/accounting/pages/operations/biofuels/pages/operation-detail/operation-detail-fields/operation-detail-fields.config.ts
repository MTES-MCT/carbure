import { MappingField } from "./operation-detail-fields.types"
import { OperationType } from "accounting/types"

/**
 * Field mapping configuration for operation details.
 *
 * This configuration-based approach allows us to specify which fields should be displayed
 * for each operation type, avoiding the need to write conditional logic scattered throughout
 * the codebase. Instead of checking the operation type for each field individually, we define
 * the fields to display declaratively here.
 *
 * The mappings are separated by receiver and sender operations to differentiate which fields
 * should be displayed when receiving an operation versus when sending an operation.
 */

/**
 * Field mappings for operations when receiving them (operations with positive quantity).
 * For each operation type, specify the list of fields that should be displayed when receiving.
 */
export const MAPPING_FIELDS_RECEIVER: MappingField[] = [
  { type: OperationType.TRANSFERT, fields: [] },
]

/**
 * Field mappings for operations when sending them (operations with negative quantity).
 * For each operation type, specify the list of fields that should be displayed when sending.
 */
export const MAPPING_FIELDS_SENDER: MappingField[] = [
  {
    type: OperationType.TRANSFERT,
    fields: [],
  },
]
