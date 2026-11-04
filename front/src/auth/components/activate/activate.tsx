import { ActivationLayout } from "./activation-link"
import { useActivate } from "./activate.hooks"

export const Activate = () => {
  const content = useActivate()
  return <ActivationLayout {...content} />
}
