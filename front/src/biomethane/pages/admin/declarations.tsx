import { Main } from "common/components/scaffold"
import { SelectDsfr } from "common/components/selects2"
import { Text } from "common/components/text"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { getBiomethaneProducers } from "./api"
import useEntity from "common/hooks/entity"
import { useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"
import { usePrivateNavigation } from "common/layouts/navigation"

const BiomethaneAdminDeclarationsPage = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const navigate = useNavigate()
  const routes = useRoutes()
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
      <SelectDsfr
        options={producers ?? []}
        onChange={onSelectProducer}
        label={t("Rechercher un établissement")}
        placeholder={t("Sélectionner un établissement")}
        style={{ maxWidth: "460px" }}
      />
    </Main>
  )
}

export default BiomethaneAdminDeclarationsPage
