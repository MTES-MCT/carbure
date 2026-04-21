import { useTranslation } from "react-i18next"

const BIOMETHANE_MODULE = "biomethane"
const BACKEND_INPUTS_NAMESPACE = "backend_inputs"

export const useBiomethaneBackendInputLabel = () => {
  const { t } = useTranslation()

  return (key: string) =>
    t(`${BIOMETHANE_MODULE}.${key}`, {
      ns: BACKEND_INPUTS_NAMESPACE,
    })
}
