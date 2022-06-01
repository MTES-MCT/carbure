import i18n from "i18n"
import format from "date-fns/intlFormat"
import formatDistanceToNow from "date-fns/formatDistanceToNow"
import fr from "date-fns/locale/fr"
import en from "date-fns/locale/en-GB"

export function formatPeriod(period: number | string) {
  const num = typeof period === "string" ? parseInt(period) : period
  return `${Math.floor(num / 100)}-${("0" + (num % 100)).slice(-2)}`
}

export function formatNumber(num: number) {
  return parseFloat(num.toFixed(2)).toLocaleString("fr-FR")
}

export function formatPercentage(num: number) {
  return formatNumber(num) + "%"
}

export function formatGHG(num: number) {
  return formatNumber(num) + " gCO2eq/MJ"
}

export function formatDate(
  date: Date | string | null,
  options: Parameters<typeof format>[1] = {}
) {
  if (date === null) {
    return "N/A"
  }

  try {
    const formatted = format(
      new Date(date),
      {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        ...options,
      },
      { locale: i18n.language === "en" ? "en-GB" : "fr" }
    )

    return formatted
  } catch (e) {
    return "N/A"
  }
}

export function formatDateYear(date: Date | string | null) {
  return formatDate(date, { month: undefined, day: undefined })
}

export function formatDateTime(date: Date | string | null) {
  return formatDate(date, {
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function formatElapsedTime(date: Date | string | null) {
  if (date === null) return ""

  return formatDistanceToNow(new Date(date), {
    addSuffix: true,
    locale: i18n.language === "en" ? en : fr,
  })
}

export function formatDeadline(deadline: Date | string | null) {
  return formatDate(deadline, { month: "long", year: undefined })
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
  }
}
