import { usePrivateNavigation } from "common/layouts/navigation"
import { TallyForm } from "common/molecules/tally-form"
import { useTranslation } from "react-i18next"

const ContactPage = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Contact"))

  return <TallyForm url="https://contact.carbure.beta.gouv.fr/contact" />
}

export default ContactPage
