import add from "date-fns/add"
import { useCallback, useState } from "react"

export interface Period {
  year: number
  month: number
}

function toDate(period: Period) {
  return Date.parse(`${period.year}-${period.month}-01`)
}

function toPeriod(date: Date): Period {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  return { year, month }
}

function getCurrentPeriod() {
  return toPeriod(new Date())
}

export function prevPeriod(period: Period) {
  const date = toDate(period)
  const prev = add(date, { months: -1 })
  return toPeriod(prev)
}

export function nextPeriod(period: Period) {
  const date = toDate(period)
  const next = add(date, { months: +1 })
  return toPeriod(next)
}

export function prettyPeriod(period: Period) {
  return `${("0" + period.month).slice(-2)} / ${period.year}`
}

export function stdPeriod(period: Period) {
  return `${period.year}-${("0" + period.month).slice(-2)}`
}

export function comparePeriod(a: Period, b: Period) {
  return `${a.year}-${a.month}` > `${b.year}-${b.month}` ? 1 : -1
}

export interface PeriodHook extends Period {
  prev: () => void
  next: () => void
  reset: () => void
}

export default function usePeriod(): PeriodHook {
  const [period, setPeriod] = useState(getCurrentPeriod)

  const prev = useCallback(() => {
    setPeriod(prevPeriod(period))
  }, [period])

  const next = useCallback(() => {
    setPeriod(nextPeriod(period))
  }, [period])

  const reset = useCallback(() => {
    setPeriod(getCurrentPeriod())
  }, [])

  return {
    ...period,
    prev,
    next,
    reset,
  }
}
