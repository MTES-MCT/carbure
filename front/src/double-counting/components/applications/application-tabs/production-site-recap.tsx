import { findCountries } from "common/api"
import { Autocomplete } from "common/components/autocomplete2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Col, Grid } from "common/components/scaffold"
import { GESOption, ProductionSiteDetails } from "common/types"
import { normalizeCountry, normalizeFeedstock } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
export const ProductionSiteRecap = ({
  productionSite,
}: {
  productionSite: ProductionSiteDetails
}) => {
  const { t } = useTranslation()
  const gesOptions = [
    { value: GESOption.Default, label: t("Valeurs par défaut") },
    { value: GESOption.NUTS2, label: t("Valeurs NUTS2") },
    { value: GESOption.Actual, label: t("Valeurs réelles") },
  ]
  return (
    <>
      <Grid>
        <TextInput
          autoFocus
          label={t("Nom du site")}
          value={productionSite.name}
          readOnly
        />
        <TextInput
          readOnly
          label={t("N° d'identification (SIRET)")}
          value={productionSite.site_siret ?? ""}
        />
        <TextInput
          readOnly
          type="date"
          label={t("Date de mise en service")}
          value={productionSite.date_mise_en_service ?? ""}
        />
      </Grid>

      <Col>
        <TextInput
          readOnly
          label={t("Adresse postale")}
          value={productionSite.address}
        />
        <Grid>
          <TextInput readOnly label={t("Ville")} value={productionSite.city} />
          <TextInput
            readOnly
            label={t("Code postal")}
            value={productionSite.postal_code}
          />
          <Autocomplete
            readOnly
            label={t("Pays")}
            placeholder={t("Rechercher un pays...")}
            getOptions={findCountries}
            normalize={normalizeCountry}
            value={productionSite.country}
          />
        </Grid>
      </Col>
      <Grid>
        <TextInput
          readOnly
          label={t("Nom du gérant")}
          value={productionSite.manager_name}
        />
        <TextInput
          readOnly
          label={t("N° de téléphone du gérant")}
          value={productionSite.manager_phone}
        />
        <TextInput
          readOnly
          label={t("Addresse email du gérant")}
          value={productionSite.manager_email}
        />
      </Grid>
      <Grid>
        <TextInput
          readOnly
          label={t("Éligible double-comptage ?")}
          value={productionSite.eligible_dc ? t("Oui") : t("Non")}
        />
        {productionSite.eligible_dc && (
          <TextInput
            readOnly
            label={t("Référence double-comptage")}
            value={productionSite.dc_reference}
          />
        )}
      </Grid>
      <RadioGroup
        label={t("Options GES")}
        options={gesOptions}
        value={productionSite.ges_option ?? GESOption.Default}
        readOnly
        orientation="horizontal"
      />
      <TextInput
        readOnly
        label={t("Matieres premieres")}
        value={productionSite.inputs
          .map((input) => normalizeFeedstock(input).label)
          .join(", ")}
      />
    </>
  )
}
