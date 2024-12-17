/**
 * This script retrieves the YAML schema generated by the backend
 * and adds additional information to simplify typing in the frontend.
 */

import fs from "fs"
import { mergeDeepRight } from "ramda"
import { parse, stringify } from "yaml"

const file = fs.readFileSync(
  new URL("../../api-schema.yaml", import.meta.url),
  "utf8"
)
const parsed = parse(file)

const res = mergeDeepRight(parsed, {
  components: {
    schemas: {
      EntityTypeEnum: {
        "x-enum-varnames": [
          "Producer",
          "Operator",
          "Administration",
          "Trader",
          "Auditor",
          "ExternalAdmin",
          "CPO",
          "Airline",
          "Unknown",
          "PowerOrHeatProducer",
        ],
      },
      UserRightsRequestsStatusEnum: {
        "x-enum-varnames": [
          "Pending", //
          "Accepted",
          "Rejected",
          "Revoked",
        ],
      },
      RoleEnum: {
        "x-enum-varnames": [
          "ReadOnly", //
          "ReadWrite",
          "Admin",
          "Auditor",
        ],
      },
    },
  },
})

fs.writeFileSync(
  new URL("../../api-schema.yaml", import.meta.url),
  stringify(res),
  "utf-8"
)
