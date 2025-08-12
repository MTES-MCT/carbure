import i18n from "i18n"
import { format as formatTime, formatDistanceToNow } from "date-fns"
import { fr, enGB as en } from "date-fns/locale"
import { ExtendedUnit, Unit } from "common/types"
import i18next from "i18next"

export function formatPeriod(period: number | string) {
  const num = typeof period === "string" ? parseInt(period) : period
  return `${Math.floor(num / 100)}-${("0" + (num % 100)).slice(-2)}`
}

export function formatPeriodFromDate(date: Date) {
  return date.getFullYear() * 100 + date.getMonth() + 1
}

export type FormatNumberOptions = {
  fractionDigits?: number
  mode?: "round" | "ceil" | "floor"
  // Add zeros to the number if it is less than the fractionDigits
  appendZeros?: boolean
}

export function formatNumber(
  num: number,
  customOptions: FormatNumberOptions = {}
) {
  const defaultOptions: FormatNumberOptions = {
    fractionDigits: 2,
    mode: "floor",
    appendZeros: true,
  }
  const { fractionDigits, mode, appendZeros } = {
    ...defaultOptions,
    ...customOptions,
  }
  const integer = Math[mode ?? "floor"](num).toFixed(0)
  let decimal = num % 1

  // add space to separate thousands
  let numStr = chunk(integer, 3).join(" ")
  if (!fractionDigits) return numStr

  if (decimal !== 0) {
    if (decimal < 0) decimal = -decimal
    let decimalStr = decimal.toFixed(fractionDigits).slice(2)
    if (!appendZeros) {
      decimalStr = decimalStr.replace(/\.?0+$/, "")
    }
    numStr += decimalStr ? "," + decimalStr : decimalStr
  }

  return numStr
}

export function roundNumber(num: number, fractionDigits = 2) {
  const factor = Math.pow(10, fractionDigits)
  return Math.round(num * factor) / factor
}

export function ceilNumber(num: number, fractionDigits = 2) {
  const factor = Math.pow(10, fractionDigits)
  return Math.ceil(num * factor) / factor
}

export const floorNumber = (num: number, fractionDigits = 2) => {
  const factor = Math.pow(10, fractionDigits)
  return Math.floor(num * factor) / factor
}

export function formatPercentage(num: number) {
  return formatNumber(num) + "%"
}

export function formatCelsiusDegree(num: number) {
  return formatNumber(num) + " °C"
}

export function formatUnit(
  num: number,
  unit: Unit | ExtendedUnit,
  customOptions: FormatNumberOptions = {}
) {
  const defaultOptions: FormatNumberOptions = {
    fractionDigits: 2,
  }
  const options = { ...defaultOptions, ...customOptions }
  const unitLabel = {
    [Unit.l]: i18next.t("litres", { count: num }),
    [Unit.kg]: i18next.t("kg"),
    [Unit.MJ]: i18next.t("MJ"),
    [ExtendedUnit.GJ]: i18next.t("GJ"),
    [ExtendedUnit.MWh]: i18next.t("MWh"),
  }

  return `${formatNumber(num, options)} ${unitLabel[unit]}`
}

export function formatUnitOnly(unit: Unit | ExtendedUnit, count = 2) {
  const unitLabel = {
    [Unit.l]: i18next.t("litres", { count }),
    [Unit.kg]: i18next.t("kg"),
    [Unit.MJ]: i18next.t("MJ"),
    [ExtendedUnit.GJ]: i18next.t("GJ"),
    [ExtendedUnit.MWh]: i18next.t("MWh"),
  }

  return unitLabel[unit]
}

export function formatGHG(num: number) {
  return formatNumber(num) + " gCO2eq/MJ"
}

export function formatDate(date: Date | string | null, format = "dd/MM/yyyy") {
  if (date === null) {
    return "N/A"
  }

  try {
    const formatted = formatTime(new Date(date), format, {
      locale: i18n.language === "fr" ? fr : en,
    })

    return formatted
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    return "N/A"
  }
}

export function formatDateYear(date: Date | string | null) {
  return formatDate(date, "yyyy")
}

export function formatDateTime(date: Date | string | null) {
  return formatDate(date, "dd/MM/yyyy HH:mm")
}

export function formatElapsedTime(date: Date | string | null) {
  if (date === null) return ""

  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
    locale: i18n.language === "fr" ? fr : en,
  })
}

export function formatDeadline(deadline: Date | string | null) {
  return formatDate(deadline, "dd MMMM")
}

// prepare string for comparison by putting it to lowercase and removing accents
export function standardize(str: string) {
  if (!str) return ""
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
}

export function capitalize(str: string) {
  return str[0]?.toUpperCase() + str.slice(1)
}

export function variations(count: number) {
  return (labels: { zero?: string; one: string; many: string }) => {
    if (count === 0) return labels.zero ?? "N/A"
    if (count === 1) return labels.one
    if (count > 1) return labels.many
    else return ""
  }
}

export function chunk(str: string, size: number): string[] {
  const chunks: string[] = []
  let chunk = ""

  for (let i = 1; i <= str.length; i++) {
    const char = str[str.length - i]
    chunk = char + chunk

    if (i % size === 0 || i === str.length) {
      chunks.push(chunk)
      chunk = ""
    }
  }

  return chunks.reverse()
}

export function formatMonth(month: number) {
  const date = new Date(0, month - 1, 1)
  const formatted = formatDate(date, "MMMM")
  return formatted.charAt(0).toUpperCase() + formatted.slice(1)
}

export const CONVERSIONS = {
  energy: {
    MJ_TO_GJ: (value: number) => value / 1000,
    GJ_TO_MJ: (value: number) => value * 1000,
  },
  euros: {
    centsToKEuros: (value: number) => parseFloat((value / 100000).toFixed(2)),
  },
}
