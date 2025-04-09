import { RadioGroup, TextInput } from "common/components/inputs2"
import { Grid } from "common/components/scaffold"
import { GESOption, ProductionSiteDetails } from "common/types"
import { getYesNoOptions, normalizeFeedstock } from "common/utils/normalizers"
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
      <Grid cols={2} gap="lg">
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
        <TextInput
          readOnly
          label={t("Adresse postale, CP, Pays")}
          value={`${productionSite.address}, ${productionSite.postal_code}, ${productionSite.country.name}`}
        />
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
      <RadioGroup
        label={t("Éligible double-comptage ?")}
        options={getYesNoOptions()}
        value={productionSite.eligible_dc}
        readOnly
        orientation="horizontal"
        small
      />

      {productionSite.eligible_dc && (
        <TextInput
          readOnly
          label={t("Référence double-comptage")}
          value={productionSite.dc_reference}
        />
      )}
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
      <TextInput
        readOnly
        label={t("Biocarburants")}
        value={productionSite.outputs
          .map((output) => normalizeFeedstock(output).label)
          .join(", ")}
      />
      <TextInput
        readOnly
        label={t("Certificats (2BS, ISCC)")}
        value={productionSite.certificates
          .map((certificate) => certificate.certificate_id)
          .join(", ")}
      />
    </>
  )
}
