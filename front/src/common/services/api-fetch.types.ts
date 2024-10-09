import type { paths, components } from "api-schema" // generated by openapi-typescript
import { FetchResponse } from "openapi-fetch"

// Remove the prefix "/api" for each path
export type newPaths = {
  [K in keyof paths as K extends `/api${infer Rest}` ? Rest : never]: paths[K]
}

/**
 * When a function that returns data from the backend is used as a generic parameter in a component,
 * the type necessary is the following (see useYears hook for example)
 */
export type DefaultResponseType<
  DataType,
  ContentType extends `${string}/${string}` = "application/json",
> = {
  responses: {
    200: {
      content: {
        [key in ContentType]: DataType
      }
    }
    400: {
      content: {
        [key in ContentType]: components["schemas"]["ErrorResponse"]
      }
    }
  }
}

export type FetchResponseType<
  DataType,
  ContentType extends `${string}/${string}` = "application/json",
> = FetchResponse<
  DefaultResponseType<DataType, ContentType>,
  unknown,
  ContentType
>

/**
 * The list of component types returned by the api
 */
export type apiTypes = components["schemas"]

/**
 * Type used for download function
 */
export type PathsWithGetMethod = {
  [Pathname in keyof newPaths]: newPaths[Pathname] extends {
    get: any
  }
    ? Pathname
    : never
}[keyof newPaths]

/**
 * Type used for download function
 */
export type QueryParams<Path extends PathsWithGetMethod> =
  newPaths[Path] extends {
    get: { parameters: { query: infer P } }
  }
    ? P
    : never
