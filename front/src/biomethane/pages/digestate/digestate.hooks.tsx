import { createContext, useContext, ReactNode } from "react"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveDigestate } from "./api"
import { BiomethaneDigestate, BiomethaneDigestatePatchRequest } from "./types"

interface DigestateContextValue {
  year: number
  saveDigestate: ReturnType<
    typeof useMutation<
      ReturnType<typeof saveDigestate>,
      [BiomethaneDigestatePatchRequest]
    >
  >
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

  const saveDigestateMutation = useMutation(
    (data: BiomethaneDigestatePatchRequest) =>
      saveDigestate(entity.id, year, data),
    {
      invalidates: ["digestate"],
      onSuccess: () => {
        notify(t("Le digestat a bien été mis à jour."), { variant: "success" })
      },
      onError: (e) => {
        notifyError(e)
      },
    }
  )

  const contextValue: DigestateContextValue = {
    year,
    saveDigestate: saveDigestateMutation,
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
