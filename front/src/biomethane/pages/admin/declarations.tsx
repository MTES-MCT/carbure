import { Grid, Main } from "common/components/scaffold"
import { Text } from "common/components/text"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  downloadBiomethaneAdminAnnualDeclaration,
  getBiomethaneProducers,
} from "./api"
import useEntity from "common/hooks/entity"
import { useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"
import { usePrivateNavigation } from "common/layouts/navigation"
import { Autocomplete } from "common/components/autocomplete2"
import { getAnnualDeclarationYearsAdmin } from "./hooks/use-annual-declaration-years-admin"
import { AnnualDeclarationExportCard } from "biomethane/components/annual-declaration-export-card"
import { useBiomethanePermissions } from "biomethane/hooks/use-biomethane-permissions"

const BiomethaneAdminDeclarationsPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const routes = useRoutes()
  const years = getAnnualDeclarationYearsAdmin()
  const { adminPermissions } = useBiomethanePermissions()
  usePrivateNavigation(t("Déclarations par établissement"))

  const { result: producers } = useQuery(
    () =>
      getBiomethaneProducers(entity.id).then((producers) =>
        producers.map((producer) => ({
          label: producer.name,
          value: producer.id.toString(),
        }))
      ),
    {
      key: "biomethane-producers",
      params: [],
    }
  )

  const onSelectProducer = (producerId?: string) => {
    if (producerId) {
      navigate(
        routes.BIOMETHANE().ADMIN.DECLARATION_DETAIL(Number(producerId)).ROOT
      )
    }
  }

  return (
    <Main>
      <Text>
        {t(
          "Veuillez sélectionner un établissement afin de voir ses déclarations et ses informations administratives et de contact."
        )}
      </Text>
      <Autocomplete
        options={producers ?? []}
        onChange={onSelectProducer}
        label={t("Rechercher un établissement")}
        placeholder={t("Rechercher un établissement")}
        style={{ maxWidth: "460px" }}
      />
      {adminPermissions.canDownloadDeclaration && (
        <Grid cols={3} gap="lg">
          {years.map((year) => (
            <AnnualDeclarationExportCard
              key={year}
              year={year}
              fileDescription={t(
                "Liste des déclarations pour l'année {{year}}",
                {
                  year,
                }
              )}
              onDownload={() =>
                downloadBiomethaneAdminAnnualDeclaration(entity.id, year)
              }
            />
          ))}
        </Grid>
      )}
    </Main>
  )
}

export default BiomethaneAdminDeclarationsPage
