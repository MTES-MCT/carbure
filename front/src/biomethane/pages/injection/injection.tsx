import { useTranslation } from "react-i18next"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
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
import { UniqueIdentificationNumberHelper } from "./components/unique-identification-number-helper"
import { useMissingFields } from "biomethane/components/missing-fields"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

type InjectionSiteForm = Partial<BiomethaneInjectionSiteAddRequest>

const BiomethaneInjectionContent = () => {
  const { t } = useTranslation()
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const allowedToEdit = useAllowedToEdit()

  const form = useForm<InjectionSiteForm>({
    city: "",
    company_address: "",
    postal_code: "",
  })
  const { value, setValue, bind } = form

  useMissingFields(form)
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
    <ManagedEditableCard
      sectionId="injection-site"
      title={t("Site d'injection")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={() => updateInjectionSite(value)}>
          <TextInput
            label={tBiomethaneInput("injection.unique_identification_number")}
            hintText={<UniqueIdentificationNumberHelper />}
            {...bind("unique_identification_number")}
            required
            readOnly={!isEditing}
          />

          <RadioGroup
            options={yesNoOptions}
            {...bind("is_shared_injection_site")}
            label={tBiomethaneInput("injection.is_shared_injection_site")}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          {value.is_shared_injection_site && (
            <TextInput
              label={tBiomethaneInput("injection.meter_number")}
              {...bind("meter_number")}
              required
              readOnly={!isEditing}
            />
          )}
          <RadioGroup
            options={yesNoOptions}
            {...bind("is_different_from_production_site")}
            label={tBiomethaneInput(
              "injection.is_different_from_production_site"
            )}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          {value.is_different_from_production_site && (
            <>
              <TextInput
                label={tBiomethaneInput("injection.company_address")}
                {...bind("company_address")}
                readOnly={!isEditing}
                required
              />
              <Grid cols={2} gap="lg">
                <TextInput
                  label={tBiomethaneInput("injection.postal_code")}
                  {...bind("postal_code")}
                  required
                  readOnly={!isEditing}
                />
                <TextInput
                  label={tBiomethaneInput("injection.city")}
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
            label={tBiomethaneInput("injection.network_type")}
            required
            readOnly={!isEditing}
            orientation="horizontal"
          />
          <TextInput
            label={tBiomethaneInput("injection.network_manager_name")}
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
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}

export const BiomethaneInjectionPage = () => {
  return (
    <SectionsManagerProvider>
      <BiomethaneInjectionContent />
    </SectionsManagerProvider>
  )
}
