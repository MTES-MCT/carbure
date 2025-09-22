import { TariffReference } from "../../types"

export const getSignatureDateConstraints = (
  tariffReference?: TariffReference | null
) => {
  if (!tariffReference) {
    return {}
  }

  switch (tariffReference) {
    case TariffReference.Value2011:
      return {
        min: "2011-11-23",
        max: "2020-11-23",
      }
    case TariffReference.Value2020:
      return {
        min: "2020-11-23",
        max: "2021-12-13",
      }
    case TariffReference.Value2021:
      return {
        min: "2021-12-13",
        max: "2023-06-10",
      }
    case TariffReference.Value2023:
      return {
        min: "2023-06-10",
      }
    default:
      return {}
  }
}
