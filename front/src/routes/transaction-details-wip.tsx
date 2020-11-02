import React from "react"

import {
  Box,
  Main,
  Title,
  Button,
  LabelInput,
  Input,
} from "../components/system"
import { Alert } from "../components/system/alert"
import {
  AlertCircle,
  Back,
  ChevronDown,
  Return,
  Save,
} from "../components/system/icons"
import Modal from "../components/system/modal"
import Select from "../components/system/select"

function createStyleSheet<T extends { [key: string]: React.CSSProperties }>(
  styles: T
): { [key in keyof T]: React.CSSProperties } {
  return styles
}

const styles = createStyleSheet({
  modal: {
    maxWidth: 1080,
  },

  detailsHeaderContainer: {
    // padding: "32px 120px",
    marginRight: 32,
    marginBottom: 32,
    // background: "var(--gray-light)",
    // marginTop: 1
    // boxShadow: "0 0 2px var(--gray-medium)",
    justifyContent: "center",
  },

  detailsHeader: {
    flex: 1,
    // maxWidth: 1080,
    // justifyContent: "space-between",
    alignItems: "center",
    position: "relative",
  },

  backButton: {
    display: "none",
    position: "absolute",
    left: -36,
    cursor: "pointer",
  },

  actionButton: {
    fontSize: 14,
    alignSelf: "center",
    marginLeft: 32,
  },

  detailsBody: {
    // margin: "24px 120px",
    // maxWidth: 1080,
    alignSelf: "center",
    marginBottom: 32,
  },

  detailsErrors: {
    marginBottom: 24,
    padding: 16,

    position: "relative" as "relative",
    flexDirection: "column" as "column",
    alignItems: "flex-start",
  },

  detailsErrorList: {
    padding: "4px 16px",
    margin: 0,
  },

  detailsComments: {
    position: "relative",
    flexDirection: "column",
    alignItems: "flex-start",
    padding: 16,
    marginBottom: 24,
  },

  detailsAlertTitle: {
    fontSize: 18,
    marginBottom: 8,
  },

  detailsCommentsSeparator: {
    border: "none",
    backgroundColor: "var(--orange-medium)",
    width: "100%",
    height: 1,
    marginTop: 0,
    marginBottom: 8,
  },

  detailsCommentsCollapser: {
    position: "absolute" as "absolute",
    top: 8,
    right: 4,
    cursor: "pointer" as "pointer",
  },

  detailsSection: {
    backgroundColor: "var(--white)",
    border: "1px solid var(--gray-highlight)",
    padding: 32,
    marginBottom: 24,
  },

  detailsSectionLeftColumn: {
    flex: 1,
    marginRight: 32,
  },

  detailsSectionRightColumn: {
    flex: 1,
  },

  detailsSectionTitle: {
    marginBottom: 24,
  },

  link: {
    color: "var(--blue-medium)",
    textDecoration: "underline",
    marginBottom: 16,
    cursor: "pointer",
    fontSize: 13,
  },

  error: {
    color: "var(--red-dark)",
    fontSize: 12,
    marginTop: -8,
    marginBottom: 8,
  },

  saveError: {
    color: "var(--red-dark)",
    fontSize: 14,
    marginBottom: 16,
  },
})

const TransactionDetails = () => {
  return (
    <Modal onClose={() => {}} style={styles.modal}>
      <Box row style={styles.detailsHeaderContainer}>
        <Box row style={styles.detailsHeader}>
          <Back style={styles.backButton} />
          <Title>Détails de la transaction #1456</Title>
          <Select
            level="primary"
            style={styles.actionButton}
            value={null}
            placeholder="Actions"
            options={[
              { value: 0, label: "Envoyer" },
              { value: 1, label: "Supprimer" },
            ]}
            onChange={() => null}
          />
        </Box>
      </Box>

      <Box style={styles.detailsBody}>
        <Alert level="error" style={styles.detailsErrors}>
          <Title style={styles.detailsAlertTitle}>
            Erreurs de validation (2)
          </Title>

          <ul style={styles.detailsErrorList}>
            <li>
              Le biocarburant n'est pas compatible avec la matière première
            </li>
            <li>La réduction de GES devrait être supérieure à 50%</li>
          </ul>

          <ChevronDown style={styles.detailsCommentsCollapser} />
        </Alert>

        <Alert level="warning" style={styles.detailsComments}>
          <Title style={styles.detailsAlertTitle}>Commentaires (3)</Title>

          <table>
            <tr>
              <td style={{ textAlign: "right", fontWeight: "bold" }}>
                Commentateur A:
              </td>
              <td>Ce lot n'a pas les bonnes informations</td>
            </tr>
            <tr>
              <td style={{ textAlign: "right", fontWeight: "bold" }}>
                Commentateur B:
              </td>
              <td>Merci, je répare ça.</td>
            </tr>
            <tr>
              <td style={{ textAlign: "right", fontWeight: "bold" }}>
                Commentateur A:
              </td>
              <td>C'est bon c'est réparé !</td>
            </tr>
          </table>

          <Box row style={{ marginTop: 16, width: "100%" }}>
            <Input placeholder="Entrer un commentaire..." />
            <Button>Envoyer</Button>
          </Box>

          <ChevronDown style={styles.detailsCommentsCollapser} />
        </Alert>

        <Box as="form">
          <Box row style={styles.detailsSection}>
            <Box style={styles.detailsSectionLeftColumn}>
              <Title style={styles.detailsSectionTitle}>Lot</Title>
              <span>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </span>
            </Box>
            <Box style={styles.detailsSectionRightColumn}>
              <LabelInput label="Volume à 20°C en Litres" type="number" />
              <LabelInput
                label="Biocarburant"
                placeholder="Rechercher un biocarburant..."
              />
              <LabelInput
                label="Matière première"
                placeholder="Rechercher une matière première..."
              />
              <LabelInput
                label="Pays d'origine"
                placeholder="Rechercher un pays..."
              />
            </Box>
          </Box>

          <Box row style={styles.detailsSection}>
            <Box style={styles.detailsSectionLeftColumn}>
              <Title style={styles.detailsSectionTitle}>Provenance</Title>
              <span>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </span>
            </Box>
            <Box style={styles.detailsSectionRightColumn}>
              <LabelInput
                label="Producteur"
                placeholder="Rechercher un producteur sur Carbure..."
              />
              <span style={styles.link}>
                Le producteur n'est pas enregistré sur Carbure ?
              </span>
              <LabelInput
                label="Site de production"
                placeholder="Rechercher un site de production sur Carbure..."
              />
              <span style={styles.link}>
                Le site de production n'est pas enregistré sur Carbure ?
              </span>
            </Box>
          </Box>

          <Box row style={styles.detailsSection}>
            <Box style={styles.detailsSectionLeftColumn}>
              <Title style={styles.detailsSectionTitle}>Destination</Title>
              <span>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </span>
            </Box>
            <Box style={styles.detailsSectionRightColumn}>
              <LabelInput
                label="Numéro douanier"
                error="Merci de renseigner un numéro de douane"
              />
              <span style={styles.error}>
                Merci de renseigner un numéro de douane
              </span>
              <LabelInput label="Date de livraison" type="date" />
              <LabelInput
                label="Client"
                placeholder="Rechercher un client sur Carbure..."
              />
              <span style={styles.link}>
                Le client n'est pas enregistré sur Carbure ?
              </span>
              <LabelInput
                label="Site de livraison"
                placeholder="Rechercher un site de livraison sur Carbure..."
              />
              <span style={styles.link}>
                Le site de livraison n'est pas enregistré sur Carbure ?
              </span>
            </Box>
          </Box>

          <Box row style={styles.detailsSection}>
            <Box style={styles.detailsSectionLeftColumn}>
              <Title style={styles.detailsSectionTitle}>
                Gaz à effet de serre
              </Title>
              <span>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </span>
            </Box>
            <Box row style={styles.detailsSectionRightColumn}>
              <Box style={{ flex: 1, marginRight: 16 }}>
                <span
                  style={{
                    fontSize: 14,
                    fontWeight: "bold",
                    textAlign: "center",
                  }}
                >
                  Émissions
                </span>
                <LabelInput label="EEC" type="number" />
                <LabelInput label="EL" type="number" />
                <LabelInput label="EP" type="number" />
                <LabelInput label="ETD" type="number" />
                <LabelInput label="EU" type="number" />
              </Box>
              <Box style={{ flex: 1 }}>
                <span
                  style={{
                    fontSize: 14,
                    fontWeight: "bold",
                    textAlign: "center",
                  }}
                >
                  Réductions
                </span>
                <LabelInput label="ESCA" type="number" />
                <LabelInput label="ECCS" type="number" />
                <LabelInput label="ECCR" type="number" />
                <LabelInput label="EEE" type="number" />
              </Box>
            </Box>
          </Box>

          <Box style={styles.detailsSection}>
            <label style={{ fontWeight: 600 }}>
              <input type="checkbox" style={{ marginRight: 12 }} />
              Ce lot sera directement mis à consommation
            </label>
          </Box>

          <Box row style={styles.detailsSection}>
            <Button
              level="primary"
              icon={Save}
              style={{ flex: 1, marginRight: 32 }}
            >
              Enregistrer les modifications
            </Button>

            <Button icon={Return} style={{ flex: 1 }}>
              Annuler les modifcations
            </Button>
          </Box>
        </Box>

        <Alert level="error" icon={AlertCircle}>
          Le serveur n'a pas pu être contacté
        </Alert>
      </Box>
    </Modal>
  )
}

export default TransactionDetails
