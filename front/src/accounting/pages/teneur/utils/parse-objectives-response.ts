import { apiTypes } from "common/services/api-fetch.types"
import { MainObjective, Objectives, SectorObjective } from "../types"
import { enrichEnergyObjective, enrichMainObjective } from "./formatters"

type ParsedCategories = Pick<
  Objectives,
  "capped_categories" | "objectivized_categories" | "unconstrained_categories"
>

const emptyCategories = (): ParsedCategories => ({
  objectivized_categories: [],
  capped_categories: [],
  unconstrained_categories: [],
})

const parseMainObjective = (
  main?: apiTypes["MainObjective"]
): MainObjective => {
  return enrichMainObjective({
    target: main?.target ?? 0,
    teneur_declared: main?.declared_teneur ?? 0,
    pending_teneur: main?.pending_teneur ?? 0,
    quantity_available: main?.available_balance ?? 0,
    target_percent: main?.target_percent ? main.target_percent * 100 : 0,
    penalty: main?.penalty ?? 0,
    energy_basis_mj: main?.energy_basis ?? 0,
  })
}

const parseSectorObjective = (
  sector: apiTypes["ObjectiveSector"]
): SectorObjective => {
  return enrichEnergyObjective({
    code: sector.code,
    target_mj: sector.objective.target_mj ?? 0,
    teneur_declared_mj: sector.declared_teneur,
    pending_teneur_mj: sector.pending_teneur,
    quantity_available_mj: sector.available_balance,
    target_percent: (sector.objective.target_percent ?? 0) * 100,
    penalty: sector.objective.penalty ?? 0,
  })
}

const parseCategoryBase = (category: apiTypes["ObjectiveCategory"]) => {
  return enrichEnergyObjective({
    code: category.code,
    target_mj: category.objective.target_mj ?? 0,
    teneur_declared_mj: category.declared_teneur,
    pending_teneur_mj: category.pending_teneur,
    quantity_available_mj: category.available_balance,
    target_percent: (category.objective.target_percent ?? 0) * 100,
    penalty: category.objective.penalty ?? 0,
    target_type: category.objective.target_type,
  })
}

const categoryGroupByTargetType = {
  REACH: "objectivized_categories",
  CAP: "capped_categories",
} as const

const parseCategories = (
  categories: apiTypes["ObjectiveCategory"][] = []
): ParsedCategories => {
  return categories.reduce<ParsedCategories>((parsedCategories, category) => {
    if (category.objective.target_mj && category.objective.target_mj === 0) {
      return parsedCategories
    }

    const categoryObjective = parseCategoryBase(category)

    if (category.objective.target_mj === null) {
      parsedCategories.unconstrained_categories.push({
        ...categoryObjective,
        target_mj: null,
        target_percent: null,
        target_type: null,
      })
      return parsedCategories
    }

    const categoryGroup =
      categoryGroupByTargetType[
        category.objective.target_type as keyof typeof categoryGroupByTargetType
      ]

    parsedCategories[categoryGroup].push(categoryObjective)

    return parsedCategories
  }, emptyCategories())
}

export const parseObjectivesResponse = (
  objectives?: apiTypes["ObjectiveOutput"]
): Objectives => ({
  global: parseMainObjective(objectives?.main),
  sectors: objectives?.sectors.map(parseSectorObjective) ?? [],
  ...parseCategories(objectives?.categories),
})
