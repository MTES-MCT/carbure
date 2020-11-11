import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"
import useForm from "../../hooks/helpers/use-form"

import { Title, Box, Button, LabelInput } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Column, Row } from "../system/table"
import { Country, ProductionSite } from "../../services/types"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { prompt, PromptFormProps } from "../system/dialog"
import AutoComplete from "../system/autocomplete"

type ProductionSiteState = {
  name: string
  country: Country | null
  date_mise_en_service: ""
}

const ProductionSitePrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<ProductionSiteState>) => {
  const [productionSite, _, onChange] = useForm<ProductionSiteState>({
    name: "",
    country: null,
    date_mise_en_service: "",
  })

  const canSave = Boolean(
    productionSite.country &&
      productionSite.date_mise_en_service &&
      productionSite.name
  )

  return (
    <Box as="form">
      <LabelInput label="Nom du site" name="name" onChange={onChange} />

      <AutoComplete
        label="Pays"
        placeholder="Rechercher un pays..."
        name="country"
        value={productionSite.country}
        getValue={(c) => c?.code_pays ?? ""}
        getLabel={(c) => c?.name ?? ""}
        getQuery={common.findCountries}
        onChange={onChange}
      />

      <LabelInput
        type="date"
        label="Date de mise en service"
        name="date_mise_en_service"
        onChange={onChange}
      />

      {/* <b>Matieres premieres:</b> */}
      {/* <b>Biocarburants:</b> */}

      <Box row className={styles.dialogButtons}>
        <Button
          level="primary"
          icon={Plus}
          disabled={!canSave}
          onClick={() => productionSite && onConfirm(productionSite)}
        >
          Ajouter
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </Box>
    </Box>
  )
}

const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}

const PRODUCTION_SITE_COLUMNS: Column<ProductionSite>[] = [
  EMPTY_COLUMN,
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.name}</span>,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.country?.name}</span>,
  },
  {
    header: "Date de mise en service",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.date_mise_en_service}</span>,
  },
]
type ProductionSitesSettingsProps = {
  entity: EntitySelection
}

const ProductionSitesSettings = ({ entity }: ProductionSitesSettingsProps) => {
  const [requestGetProductionSites, resolveGetProductionSites] = useAPI(common.findProductionSites); // prettier-ignore

  const entityID = entity?.id
  const productionSites = requestGetProductionSites.data ?? []
  const isEmpty = productionSites.length === 0

  const columns = [
    ...PRODUCTION_SITE_COLUMNS,
    {
      className: styles.settingsTableActionColumn,
      render: () => (
        <Box row className={styles.settingsTableActions}>
          <Cross title="Supprimer le site de production" />
        </Box>
      ),
    },
  ]

  const rows: Row<ProductionSite>[] = productionSites.map((ps) => ({ value: ps })); // prettier-ignore

  async function createProductionSite() {
    const data = await prompt(
      "Ajouter un site de production",
      "Veuillez entrer les informations de votre nouveau site de production.",
      ProductionSitePrompt
    )

    // @TODO actually add the certificate
  }

  useEffect(() => {
    if (entityID) {
      resolveGetProductionSites("", entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Sites de production</Title>
        <Button level="primary" icon={Plus} onClick={createProductionSite}>
          Ajouter un site de production
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun site de production trouvé
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}
    </Section>
  )
}

export default ProductionSitesSettings
