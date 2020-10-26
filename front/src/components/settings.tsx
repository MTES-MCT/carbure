import React from "react"

import styles from "./settings.module.css"

import { Title, Box } from "./system"

type AnnuaireSettingsProps = {
    data: number
}
  
export const AnnuaireSettings = ({
    data,
}: AnnuaireSettingsProps) => (
    <Box>
        <p>Annuaire</p>
    </Box>
)

type MACSettingsProps = {
    data: number
}
  
export const MACSettings = ({
    data,
}: MACSettingsProps) => (
    <Box>
        <p>MAC</p>
    </Box>
)

  
type ProductionSitesSettingsProps = {
    data: number
}
  
export const ProductionSitesSettings = ({
    data,
}: ProductionSitesSettingsProps) => (
    <Box>
        <p>Annuaire</p>
    </Box>
)

  
type DeliverySitesSettingsProps = {
    data: number
}
  
export const DeliverySitesSettings = ({
    data,
}: DeliverySitesSettingsProps) => (
    <Box>
        <p>DeliverySites</p>
    </Box>
)

  
  
