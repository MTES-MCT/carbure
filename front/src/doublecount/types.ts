import { Entity, ProductionSite, MatierePremiere, Biocarburant, Country } from "common/types";

export enum Admin {
  DGEC = "MTE - DGEC",
  DGDDI = "DGDDI",
  DGPE = "DGPE",
}

export enum DoubleCountingStatus {
  Pending = "PENDING",
  InProgress = "INPROGRESS",
  Rejected = "REJECTED",
  Accepted = "ACCEPTED",
  Lapsed = "LAPSED",
}


export interface DoubleCounting {
  id: number
  producer: Entity
  production_site: string
  period_start: string
  period_end: string
  status: DoubleCountingStatus
  producer_user: string
  creation_date: string
}

export interface DoubleCountingSourcingAggregation {
  year: number
  sum: number
  count: number
  feedstock: MatierePremiere
}

export interface DoubleCountingSourcing {
  id: number
  year: number
  metric_tonnes: number
  feedstock: MatierePremiere
  origin_country: Country
  transit_country?: Country
  supply_country?: Country
}

export interface DoubleCountingProduction {
  id: number
  year: number
  feedstock: MatierePremiere
  biofuel: Biocarburant
  max_production_capacity?: number
  estimated_production: number
  requested_quota: number
  approved_quota: number
}

export interface DoubleCountingDetails extends DoubleCounting {
  sourcing: DoubleCountingSourcing[]
  production: DoubleCountingProduction[]
  aggregated_sourcing: DoubleCountingSourcingAggregation[]
  documents: { id: number, url: string }[]
  dgec_validated: boolean
  dgec_validator: string | null
  dgec_validated_dt: string | null
  dgddi_validated: boolean
  dgddi_validator: string | null
  dgddi_validated_dt: string | null
  dgpe_validated: boolean
  dgpe_validator: string | null
  dgpe_validated_dt: string | null
}


export interface AgreementSnapshot {
  years: number[]
}

export interface AgreementsOverview {
  accepted: { count: number, agreements: DoubleCounting[] },
  rejected: { count: number, agreements: DoubleCounting[] },
  expired: { count: number, agreements: DoubleCounting[] },
  pending: { count: number, agreements: DoubleCounting[] },
  progress: { count: number, agreements: DoubleCounting[] },
}

export interface QuotaOverview {
  producer: Entity
  production_site: ProductionSite
  approved_quota_weight_sum: number
  current_production_weight_sum: number
  nb_quotas: number
  nb_full_quotas: number
  nb_breached_quotas: number
}

export interface QuotaDetails {
  volume: number,
  approved_quota: number,
  current_production_weight_sum_tonnes: number,
  feedstock: MatierePremiere,
  biofuel: Biocarburant,
  nb_lots: number
}