/**
 * Transform binary fields to File and single-value string enums to literals.
 */
import openapiTS, { astToString } from "openapi-typescript"
import ts from "typescript"
import fs from "fs"

const FILE = ts.factory.createTypeReferenceNode(
  ts.factory.createIdentifier("File")
) // `File`
const NULL = ts.factory.createLiteralTypeNode(ts.factory.createNull()) // `null`

const ast = await openapiTS(new URL("../../api-schema.yaml", import.meta.url), {
  transform(schemaObject) {
    // Create a File type from binary
    if (schemaObject.format === "binary") {
      return schemaObject.nullable
        ? ts.factory.createUnionTypeNode([FILE, NULL])
        : FILE
    }
    if (
      schemaObject.enum?.length === 1 &&
      typeof schemaObject.enum[0] === "string"
    ) {
      const literal = ts.factory.createLiteralTypeNode(
        ts.factory.createStringLiteral(schemaObject.enum[0])
      )
      return schemaObject.nullable
        ? ts.factory.createUnionTypeNode([literal, NULL])
        : literal
    }
  },
  enum: true,
  dedupeEnums: true,
})

const contents = astToString(ast)

fs.writeFileSync(new URL("../src/api-schema.ts", import.meta.url), contents)
