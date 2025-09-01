import { createContext, useContext, ReactNode } from "react"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveDigestate } from "./api"
import { BiomethaneDigestateAddRequest } from "./types"
import { declarationInterval } from "biomethane/utils"

interface DigestateContextValue {
  year: number
  saveDigestate: ReturnType<
    typeof useMutation<
      Awaited<ReturnType<typeof saveDigestate>>,
      [BiomethaneDigestateAddRequest]
    >
  >
  isInDeclarationPeriod: boolean
}

const DigestateContext = createContext<DigestateContextValue | null>(null)

interface DigestateProviderProps {
  children: ReactNode
  year: number
}

export function DigestateProvider({ children, year }: DigestateProviderProps) {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const isInDeclarationPeriod = year === declarationInterval.year

  const saveDigestateMutation = useMutation(
    (data: BiomethaneDigestateAddRequest) => saveDigestate(entity.id, data),
    {
      invalidates: ["digestate"],
      onSuccess: () => {
        notify(t("Le digestat a bien été mis à jour."), { variant: "success" })
      },
      onError: () => notifyError(),
    }
  )

  const contextValue: DigestateContextValue = {
    year,
    saveDigestate: saveDigestateMutation,
    isInDeclarationPeriod,
  }

  return (
    <DigestateContext.Provider value={contextValue}>
      {children}
    </DigestateContext.Provider>
  )
}

export function useDigestateContext(): DigestateContextValue {
  const context = useContext(DigestateContext)
  if (!context) {
    throw new Error(
      "useDigestateContext doit être utilisé dans un DigestateProvider"
    )
  }
  return context
}
