import { apiTypes } from "common/services/api-fetch.types"
import { CONVERSIONS } from "common/utils/formatters"
import {
  CategoryObjective,
  MainObjective,
  Objectives,
  SectorObjective,
} from "../types"

type ParsedCategories = Pick<
  Objectives,
  "capped_categories" | "objectivized_categories" | "unconstrained_categories"
>

const toGj = CONVERSIONS.energy.MJ_TO_GJ

const emptyCategories = (): ParsedCategories => ({
  objectivized_categories: [],
  capped_categories: [],
  unconstrained_categories: [],
})

const parseMainObjective = (
  main?: apiTypes["MainObjective"]
): MainObjective => ({
  target: main?.target ?? 0,
  teneur_declared: main?.declared_teneur ?? 0,
  pending_teneur: main?.pending_teneur ?? 0,
  quantity_available: main?.available_balance ?? 0,
  target_percent: main?.target_percent ? main.target_percent * 100 : 0,
  penalty: main?.penalty ?? 0,
  energy_basis: toGj(main?.energy_basis ?? 0),
})

const parseSectorObjective = (
  sector: apiTypes["ObjectiveSector"]
): SectorObjective => ({
  code: sector.code,
  target: toGj(sector.objective.target_mj),
  teneur_declared: toGj(sector.declared_teneur),
  pending_teneur: toGj(sector.pending_teneur),
  quantity_available: toGj(sector.available_balance),
  target_percent: sector.objective.target_percent * 100,
  penalty: sector.objective.penalty ?? 0,
})

const parseCategoryBase = (category: apiTypes["ObjectiveCategory"]) => ({
  code: category.code,
  target: category.objective.target_mj ? toGj(category.objective.target_mj) : 0,
  teneur_declared: toGj(category.declared_teneur),
  pending_teneur: toGj(category.pending_teneur),
  quantity_available: toGj(category.available_balance),
  target_percent: category.objective.target_percent * 100,
  penalty: category.objective.penalty ?? 0,
})

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

    if (!category.objective.target_mj) {
      parsedCategories.unconstrained_categories.push({
        ...categoryObjective,
        target: null,
        target_percent: null,
      })
      return parsedCategories
    }

    const categoryGroup =
      categoryGroupByTargetType[
        category.objective.target_type as keyof typeof categoryGroupByTargetType
      ]

    parsedCategories[categoryGroup].push(categoryObjective as CategoryObjective)

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
