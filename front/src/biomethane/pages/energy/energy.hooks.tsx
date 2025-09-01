import { createContext, useContext, ReactNode } from "react"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveEnergy } from "./api"
import { BiomethaneEnergyAddRequest } from "./types"
import { declarationInterval } from "biomethane/utils"

interface EnergyContextValue {
  year: number
  saveEnergy: ReturnType<
    typeof useMutation<
      Awaited<ReturnType<typeof saveEnergy>>,
      [BiomethaneEnergyAddRequest]
    >
  >
  isInDeclarationPeriod: boolean
}

const EnergyContext = createContext<EnergyContextValue | null>(null)

interface EnergyProviderProps {
  children: ReactNode
  year: number
}

export function EnergyProvider({ children, year }: EnergyProviderProps) {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const isInDeclarationPeriod = year === declarationInterval.year

  const saveEnergyMutation = useMutation(
    (data: BiomethaneEnergyAddRequest) => saveEnergy(entity.id, data),
    {
      invalidates: ["energy"],
      onSuccess: () => {
        notify(t("Les données ont bien été mises à jour."), {
          variant: "success",
        })
      },
      onError: () => notifyError(),
    }
  )

  const contextValue: EnergyContextValue = {
    year,
    saveEnergy: saveEnergyMutation,
    isInDeclarationPeriod,
  }

  return (
    <EnergyContext.Provider value={contextValue}>
      {children}
    </EnergyContext.Provider>
  )
}

export function useEnergyContext(): EnergyContextValue {
  const context = useContext(EnergyContext)
  if (!context) {
    throw new Error("useEnergyContext doit être utilisé dans un EnergyProvider")
  }
  return context
}
