import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"
import useForm from "../../hooks/helpers/use-form"

import { Title, Box, Button, LabelInput, LoaderOverlay } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Actions, Column, Line, Row } from "../system/table"
import { Country, ProductionSite } from "../../services/types"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { prompt, PromptFormProps } from "../system/dialog"
import AutoComplete from "../system/autocomplete"
import { EMPTY_COLUMN } from "."

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

const PRODUCTION_SITE_COLUMNS: Column<ProductionSite>[] = [
  EMPTY_COLUMN,
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={ps.name} />,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={ps.country?.name} />,
  },
  {
    header: "Date de mise en service",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={ps.date_mise_en_service} />,
  },
]
type ProductionSitesSettingsProps = {
  entity: EntitySelection
}

const ProductionSitesSettings = ({ entity }: ProductionSitesSettingsProps) => {
  const [requestGetProductionSites, resolveGetProductionSites] = useAPI(common.findProductionSites) // prettier-ignore
  const [requestAddProductionSite, resolveAddProductionSite] = useAPI(api.addProductionSite) // prettier-ignore

  const entityID = entity?.id
  const productionSites = requestGetProductionSites.data ?? []

  const isLoading = requestAddProductionSite.loading || requestGetProductionSites.loading // prettier-ignore
  const isEmpty = productionSites.length === 0

  const columns = [
    ...PRODUCTION_SITE_COLUMNS,
    Actions<ProductionSite>([
      {
        icon: Cross,
        title: "Supprimer le site de production",
        action: () => console.log("supprimer"),
      },
    ]),
  ]

  const rows: Row<ProductionSite>[] = productionSites.map((ps) => ({ value: ps })); // prettier-ignore

  async function createProductionSite() {
    const data = await prompt(
      "Ajouter un site de production",
      "Veuillez entrer les informations de votre nouveau site de production.",
      ProductionSitePrompt
    )

    if (entityID && data && data.country) {
      resolveAddProductionSite(
        entityID,
        data.name,
        data.date_mise_en_service,
        true,
        data.country.code_pays
      ).then(() => resolveGetProductionSites("", entityID))
    }
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

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default ProductionSitesSettings
