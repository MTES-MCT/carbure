import { usePrivateNavigation } from "common/layouts/navigation"
import { TallyForm } from "common/molecules/tally-form"
import { useTranslation } from "react-i18next"

const CustomerSatisfaction = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Enquête de satisfaction"))

  return (
    <TallyForm url="https://contact.carbure.beta.gouv.fr/biomethane/customer-satisfaction" />
  )
}

export default CustomerSatisfaction
