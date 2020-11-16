import React, { useEffect } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"
import useForm from "../../hooks/helpers/use-form"

import { Title, Box, Button, LabelInput, LoaderOverlay, Label } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Actions, Column, Line, Row } from "../system/table"
import { Country, ProductionSite } from "../../services/types"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { confirm, prompt, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete } from "../system/autocomplete"
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
  const [productionSite, hasChanged, onChange] = useForm<ProductionSiteState>({
    name: "",
    country: null,
    date_mise_en_service: "",
  })

  const canSave = Boolean(
    hasChanged &&
      productionSite.country &&
      productionSite.date_mise_en_service &&
      productionSite.name
  )

  return (
    <Box as="form">
      <LabelInput label="Nom du site" name="name" onChange={onChange} />

      <LabelAutoComplete
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

      <Label label="Matieres premieres">
        <div
          style={{
            display: "flex",
            border: "1px solid var(--blue-medium)",
            background: "var(--white)",
            minHeight: 36,
            padding: 6,
            flexWrap: "wrap",
          }}
        >
          <span
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--blue-light)",
              padding: "4px 8px",
              margin: 4,
            }}
          >
            Colza
            <Cross size={16} style={{ marginLeft: 8 }} />
          </span>
          <span
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--blue-light)",
              padding: "4px 8px",
              margin: 4,
            }}
          >
            Colza
            <Cross size={16} style={{ marginLeft: 8 }} />
          </span>
          <span
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--blue-light)",
              padding: "4px 8px",
              margin: 4,
            }}
          >
            Huiles issues de la consommation
            <Cross size={16} style={{ marginLeft: 8 }} />
          </span>
          <span
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--blue-light)",
              padding: "4px 8px",
              margin: 4,
            }}
          >
            Colza
            <Cross size={16} style={{ marginLeft: 8 }} />
          </span>
          <span
            style={{
              display: "flex",
              alignItems: "center",
              background: "var(--blue-light)",
              padding: "4px 8px",
              margin: 4,
            }}
          >
            Huiles issues de la consommation
            <Cross size={16} style={{ marginLeft: 8 }} />
          </span>

          <input
            style={{ border: "none", background: "transparent " }}
            placeholder="Ajouter une matière première"
          />
        </div>
      </Label>

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
  const [requestDelProductionSite, resolveDelProductionSite] = useAPI(api.deleteProductionSite) // prettier-ignore

  const entityID = entity?.id
  const productionSites = requestGetProductionSites.data ?? []

  const isLoading =
    requestAddProductionSite.loading ||
    requestGetProductionSites.loading ||
    requestDelProductionSite.loading

  const isEmpty = productionSites.length === 0

  function refresh() {
    if (entityID) {
      resolveGetProductionSites("", entityID)
    }
  }

  async function createProductionSite() {
    const data = await prompt(
      "Ajout site de production",
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
      ).then(refresh)
    }
  }

  async function removeProductionSite(ps: ProductionSite) {
    if (
      await confirm(
        "Suppression site",
        `Voulez-vous vraiment supprimer le site de production "${ps.name}" ?`
      )
    ) {
      resolveDelProductionSite(ps.id).then(refresh)
    }
  }

  useEffect(() => {
    if (entityID) {
      resolveGetProductionSites("", entityID)
    }
  }, [entityID, resolveGetProductionSites])

  const columns = [
    ...PRODUCTION_SITE_COLUMNS,
    Actions([
      {
        icon: Cross,
        title: "Supprimer le site de production",
        action: removeProductionSite,
      },
    ]),
  ]

  const rows: Row<ProductionSite>[] = productionSites.map((ps) => ({ value: ps })); // prettier-ignore

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
