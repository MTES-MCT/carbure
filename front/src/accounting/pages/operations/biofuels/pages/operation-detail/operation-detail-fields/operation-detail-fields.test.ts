import { describe, expect, it } from "vitest"
import {
  getFields,
  OperationDetailFields,
} from "./operation-detail-fields.utils"
import { operation } from "accounting/__test__/data/biofuels/operation"

describe("getFields", () => {
  it("Should return empty array if conditional fields are empty", () => {
    const fields = getFields(operation, [])
    expect(fields).toEqual([])
  })

  it("Should return fields for receiver operation and operation type TRANSFERT", () => {
    const fields = getFields(operation, [
      { name: OperationDetailFields.TEST, label: "Test", value: "Test" },
      { name: OperationDetailFields.SECTOR, label: "Sector", value: "Sector" },
    ])

    expect(fields).toEqual([
      { name: OperationDetailFields.TEST, label: "Test", value: "Test" },
    ])
  })

  it("Should return fields for sender operation and operation type TRANSFERT", () => {
    const fields = getFields({ ...operation, quantity: -1000 }, [
      { name: OperationDetailFields.TEST, label: "Test", value: "Test" },
      { name: OperationDetailFields.SECTOR, label: "Sector", value: "Sector" },
    ])
    expect(fields).toEqual([
      { name: OperationDetailFields.SECTOR, label: "Sector", value: "Sector" },
    ])
  })
})
