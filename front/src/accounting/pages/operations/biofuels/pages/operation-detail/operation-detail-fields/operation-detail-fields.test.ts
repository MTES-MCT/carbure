import { describe, expect, it } from "vitest"
import { getFields } from "./operation-detail-fields.utils"
import { operation } from "accounting/__test__/data/biofuels/operation"
import {
  Field,
  MappingField,
  OperationDetailField,
} from "./operation-detail-fields.types"
import { OperationType } from "accounting/types"

// Helper functions to create test fields and mapping fields by avoiding type errors
const createTestField = (
  name: string,
  label: string,
  value: string
): Field => ({
  name: name as OperationDetailField,
  label,
  value,
})

const createTestMapping = (
  type: OperationType,
  fields: string[]
): MappingField => ({
  type,
  fields: fields as OperationDetailField[],
})
describe("getFields", () => {
  it("Should return empty array if conditional fields or mapping fields are empty", () => {
    const fields = getFields(operation, [], [])
    expect(fields).toEqual([])
  })

  it("Should return only the fields that are in the mapping fields for operation type TRANSFERT", () => {
    const field1 = createTestField("TEST", "Test", "Test")
    const field2 = createTestField("TEST2", "Test 2", "Test 2")

    const fields = getFields(
      operation,
      [field1, field2],
      [createTestMapping(OperationType.TRANSFERT, ["TEST2"])]
    )

    expect(fields).toEqual([field2])
  })
})
