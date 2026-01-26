import { useTranslation } from "react-i18next"
import { EditableCard } from "common/molecules/editable-card"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { BiomethaneInjectionSiteAddRequest } from "./types"
import { useForm } from "common/components/form2"
import { Grid } from "common/components/scaffold"
import { getYesNoOptions } from "common/utils/normalizers"
import {
  useGetInjectionNetworkTypesOption,
  useGetInjectionSite,
  useMutateInjectionSite,
} from "./injection.hooks"
import { Button } from "common/components/button2"

type InjectionSiteForm = Partial<BiomethaneInjectionSiteAddRequest>
export const BiomethaneInjectionPage = () => {
  const { t } = useTranslation()

  const { value, setValue, bind } = useForm<InjectionSiteForm>({
    city: "",
    company_address: "",
    postal_code: "",
  })
  useGetInjectionSite({
    onSuccess: (data) => {
      if (data) {
        setValue(data)
      }
    },
  })
  const { execute: updateInjectionSite, loading: loadingUpdateInjectionSite } =
    useMutateInjectionSite()
  const networkTypesOptions = useGetInjectionNetworkTypesOption()
  const yesNoOptions = getYesNoOptions()

  return (
    <EditableCard title={t("Site d'injection")}>
      {({ isEditing }) => (
        <EditableCard.Form onSubmit={() => updateInjectionSite(value)}>
          <TextInput
            label={t("Numéro d'identifiant unique du site d'injection")}
            {...bind("unique_identification_number")}
            required
            readOnly={!isEditing}
          />

          <RadioGroup
            options={yesNoOptions}
            {...bind("is_shared_injection_site")}
            label={t("Raccordement à un site d'injection mutualisé")}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          {value.is_shared_injection_site && (
            <TextInput
              label={t("N° de compteur associé au site d'injection")}
              {...bind("meter_number")}
              required
              readOnly={!isEditing}
            />
          )}
          <RadioGroup
            options={yesNoOptions}
            {...bind("is_different_from_production_site")}
            label={t("Le site d'injection est différent du site de production")}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          {value.is_different_from_production_site && (
            <>
              <TextInput
                label={t("Adresse du site d'injection (Numéro et rue)")}
                {...bind("company_address")}
                readOnly={!isEditing}
                required
              />
              <Grid cols={2} gap="lg">
                <TextInput
                  label={t("Code postal")}
                  {...bind("postal_code")}
                  required
                  readOnly={!isEditing}
                />
                <TextInput
                  label={t("Commune")}
                  {...bind("city")}
                  required
                  readOnly={!isEditing}
                />
              </Grid>
            </>
          )}

          <RadioGroup
            options={networkTypesOptions}
            {...bind("network_type")}
            label={t("Type de réseau")}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          <TextInput
            label={t("Nom du gestionnaire de réseau")}
            {...bind("network_manager_name")}
            required
            readOnly={!isEditing}
          />

          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loadingUpdateInjectionSite}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </EditableCard.Form>
      )}
    </EditableCard>
  )
}
