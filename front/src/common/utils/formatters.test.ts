import { describe, expect, it } from "vitest"
import { formatNumber } from "./formatters"

describe("formatters", () => {
  describe("formatNumber", () => {
    it("Should space to separate thousands", () => {
      expect(formatNumber(1000000, { fractionDigits: 2 })).toBe("1 000 000")
    })

    it("Should handle negative number and fraction digits", () => {
      expect(formatNumber(-1000000.45, { fractionDigits: 2 })).toBe(
        "-1 000 000,45"
      )
    })

    it("Should pass options as parameter", () => {
      expect(
        formatNumber(1000000.457, {
          fractionDigits: 2,
          mode: "ceil",
        })
      ).toBe("1 000 000,46")
    })

    it("Should return the number as an integer if fractionDigits is 0", () => {
      expect(formatNumber(1000000, { fractionDigits: 0 })).toBe("1 000 000")
    })

    it("Should add zeros to the decimal part if appendZeros is true", () => {
      expect(
        formatNumber(1000000.1, {
          fractionDigits: 4,
          appendZeros: true,
        })
      ).toBe("1 000 000,1000")
    })
  })
})
