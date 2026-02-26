import { Dialog } from "common/components/dialog2"
import { Button } from "common/components/button2"
import { Text } from "common/components/text"
import { CustomStepper } from "./custom-stepper"
import { useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"
import { addQueryParams } from "common/utils/routes"
import useEntity from "common/hooks/entity"
import useLocalStorage from "common/hooks/storage"

export const useAlreadyParticipatedYears = () => {
  const [alreadyParticipatedYears, setAlreadyParticipatedYears] =
    useLocalStorage<number[] | undefined>(
      "carbure:alreadyParticipatedBiomethaneCustomerSatisfactionYears",
      new Array<number>()
    )

  const addYear = (year: number) => {
    if (alreadyParticipatedYears?.includes(year)) {
      return
    }
    alreadyParticipatedYears?.push(year)
    setAlreadyParticipatedYears(alreadyParticipatedYears)
  }

  const isAlreadyParticipated = (year: number) => {
    return alreadyParticipatedYears?.includes(year)
  }

  return {
    years: Array.from(alreadyParticipatedYears ?? []),
    addYear,
    isAlreadyParticipated,
  }
}
export const DeclarationValidatedModalStep2 = ({
  onClose,
  declarationYear,
}: {
  onClose: () => void
  declarationYear: number
}) => {
  const navigate = useNavigate()
  const routes = useRoutes()
  const entity = useEntity()
  const { addYear } = useAlreadyParticipatedYears()

  const goToCustomerSatisfaction = () => {
    onClose()

    addYear(declarationYear)

    const url = addQueryParams(
      routes.BIOMETHANE().PRODUCER.CUSTOMER_SATISFACTION,
      {
        entity: entity.name,
      }
    )
    navigate(url)
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>Participez à l’amélioration du dispositif</Dialog.Title>
      }
      footer={
        <Button priority="primary" onClick={goToCustomerSatisfaction}>
          Je participe
        </Button>
      }
      size="medium"
    >
      <Text>
        Dans une démarche d’amélioration continue et de simplification des
        démarches déclaratives, nous vous invitons à répondre à cette enquête de
        satisfaction. Votre retour est essentiel pour adapter l’outil aux
        besoins des déclarants et renforcer son efficacité.
      </Text>
      Merci pour votre contribution à la simplification des démarches et à
      l’amélioration du dispositif.
      <CustomStepper currentStep={2} totalSteps={2} />
    </Dialog>
  )
}
