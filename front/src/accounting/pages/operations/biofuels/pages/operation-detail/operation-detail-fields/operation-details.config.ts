import { MappingField } from "./operation-detail.types"
import { OperationType } from "accounting/types"

// on crée un mapping en fonction de si on a envoyé ou reçu une opération et du type d'opération
export const MAPPING_FIELDS_RECEIVER: MappingField[] = [
  { type: OperationType.TRANSFERT, fields: [] },
]

export const MAPPING_FIELDS_SENDER: MappingField[] = [
  {
    type: OperationType.TRANSFERT,
    fields: [],
  },
]
