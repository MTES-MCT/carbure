import i18n from "i18n"
import format from "date-fns/intlFormat"

export function formatPeriod(period: number) {
  return `${("0" + (period % 100)).slice(-2)} / ${Math.floor(period / 100)}`
}

export function formatNumber(volume: number) {
  return parseFloat(volume.toFixed(2)).toLocaleString("fr-FR")
}

export function formatDate(
  str: string | null,
  options: Parameters<typeof format>[1] = {}
) {
  if (str === null) {
    return "N/A"
  }

  try {
    const formatted = format(
      new Date(str),
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

// prepare string for comparison by putting it to lowercase and removing accents
export function standardize(str: string) {
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
}

export function variations(count: number) {
  return (labels: { zero: string; one: string; many: string }) => {
    if (count === 0) return labels.zero
    if (count === 1) return labels.one
    if (count > 1) return labels.many
  }
}
