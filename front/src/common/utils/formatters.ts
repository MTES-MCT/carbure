import i18n from "i18n"
import formatTime from "date-fns/format"
import formatDistanceToNow from "date-fns/formatDistanceToNow"
import fr from "date-fns/locale/fr"
import en from "date-fns/locale/en-GB"
import { Unit } from "carbure/types"
import i18next from "i18next"

export function formatPeriod(period: number | string) {
  const num = typeof period === "string" ? parseInt(period) : period
  return `${Math.floor(num / 100)}-${("0" + (num % 100)).slice(-2)}`
}

export function formatPeriodFromDate(date: Date) {
  return date.getFullYear() * 100 + date.getMonth() + 1
}

export function formatNumber(num: number, fractionDigits = 2) {
  const integer = Math.floor(num).toFixed(0)
  let decimal = num % 1

  // add space to separate thousands
  let numStr = chunk(integer, 3).join(" ")
  if (!fractionDigits) return numStr

  if (decimal !== 0) {
    if (decimal < 0) decimal = -decimal
    const decimalStr = decimal.toFixed(fractionDigits).slice(2)
    numStr += "," + decimalStr
  }

  return numStr
}

export function formatPercentage(num: number) {
  return formatNumber(num) + "%"
}

export function formatCelsiusDegree(num: number) {
  return formatNumber(num) + " °C"
}

export function formatUnit(num: number, unit: Unit) {
  const unitLabel = {
    l: i18next.t("litres", { count: num }),
    kg: i18next.t("kg"),
    MJ: i18next.t("MJ"),
  }

  return `${formatNumber(num)} ${unitLabel[unit]}`
}

export function formatGHG(num: number) {
  return formatNumber(num) + " gCO2eq/MJ"
}

export function formatDate(date: Date | string | null, format = "dd/MM/yyyy") {
  if (date === null) {
    return "N/A"
  }

  try {
    const formatted = formatTime(
      new Date(date),
      format,
      // @ts-ignore it says it only want strings but it actually doesn't
      { locale: i18n.language === "fr" ? fr : en }
    )

    return formatted
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
  return str[0].toUpperCase() + str.slice(1)
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
