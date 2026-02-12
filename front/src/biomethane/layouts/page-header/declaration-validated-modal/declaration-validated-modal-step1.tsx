import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { CustomStepper } from "./custom-stepper"
import { Text } from "common/components/text"

export const DeclarationValidatedModalStep1 = ({
  onClose,
}: {
  onClose: () => void
}) => {
  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          Votre déclaration a bien été prise en compte
        </Dialog.Title>
      }
      footer={
        <Button priority="primary" onClick={onClose}>
          Suivant
        </Button>
      }
      size="medium"
    >
      <Text>
        Merci pour la transmission de votre rapport de fonctionnement 2025 sur
        la plateforme CarbuRe. Celui-ci a été transmis aux services de l’État
        compétents, notamment à votre DREAL.
      </Text>
      <b>Utilisation des données</b>
      <Text>
        Les informations recueillies pourront être partagées, dans le respect
        des périmètres réglementaires, avec les administrations et organismes
        concernés : DGEC, CRE, DREAL, MASA et DRAAF, FranceAgriMer, ADEME, les
        Régions (sur demande via la DREAL), ainsi que votre acheteur de
        biométhane.
      </Text>
      Objectif : simplifier et mutualiser les démarches
      <Text>
        Si vous êtes sollicités par une autre entité pour des données déjà
        transmises via CarbuRe, nous vous invitons à en informer votre
        correspondant DREAL afin d’envisager un partage direct des informations
        par le biais de l’outil.
      </Text>
      <CustomStepper currentStep={1} totalSteps={2} />
    </Dialog>
  )
}
