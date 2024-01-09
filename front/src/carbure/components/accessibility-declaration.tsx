import css from "./accessibility-declaration.module.css"
import { MailTo } from "common/components/button"
import { Main, Panel } from "common/components/scaffold"

const AccessibilityDeclaration = () => {
  return (
    <Main className={css.accessibility}>
      <header>
        <h1>Déclaration d'accessibilité</h1>
      </header>
      <section>
        <Panel>
          <header>
            <p>
              Établie le <i>27 décembre 2023</i>.
            </p>
          </header>

          <section>
            <p>
              Le <strong>Ministère de l'Écologie</strong> s'engage à rendre son
              service accessible, conformément à l'article 47 de la loi n°
              2005-102 du 11 février 2005.
            </p>
            <p>
              Cette déclaration d'accessibilité s'applique à{" "}
              <strong>CarbuRe</strong>{" "}
              <span>
                (
                <a href="https://carbure.beta.gouv.fr/">
                  https://carbure.beta.gouv.fr/
                </a>
                )
              </span>
            </p>
            <p>
              À cette fin, nous mettons en œuvre la stratégie et les actions
              suivantes :{" "}
              <a
                target="_blank"
                rel="noreferrer"
                href="https://carbure-1.gitbook.io/faq/mentions-legales-et-cgu/mentions-legales-et-conditions-generales-dutilisation-1"
              >
                Schéma pluriannuel de mise en accessibilité
              </a>
            </p>
          </section>
          <section>
            <h2>État de conformité</h2>
            <p>
              <strong>CarbuRe</strong> est <strong>non conforme</strong> avec le{" "}
              <abbr title="Référentiel général d'amélioration de l'accessibilité">
                RGAA
              </abbr>
              . <span>Le site n'a encore pas été audité.</span>
            </p>
          </section>
          <section>
            <h2>Amélioration et contact</h2>
            <p>
              Si vous n'arrivez pas à accéder à un contenu ou à un service, vous
              pouvez contacter le responsable de <strong>CarbuRe</strong> pour
              être orienté vers une alternative accessible ou obtenir le contenu
              sous une autre forme.
            </p>
            <ul className="basic-information feedback h-card">
              <li>
                E-mail :{" "}
                <MailTo
                  user="carbure"
                  host="beta.gouv.fr"
                  subject="CarbuRe - Accessibilité"
                >
                  Contact CarbuRe
                </MailTo>
              </li>
              <li>
                Adresse :{" "}
                <span>
                  Tour Séquoïa 1, place Carpeaux 92055 La Défense Cedex
                </span>
              </li>
            </ul>
            <p>
              Nous essayons de répondre dans les <span>3 jours ouvrés</span>.
            </p>
          </section>
          <section>
            <h2>Voie de recours</h2>
            <p>
              Cette procédure est à utiliser dans le cas suivant : vous avez
              signalé au responsable du site internet un défaut d'accessibilité
              qui vous empêche d'accéder à un contenu ou à un des services du
              portail et vous n'avez pas obtenu de réponse satisfaisante.
            </p>
            <p>Vous pouvez :</p>
            <ul>
              <li>
                Écrire un message au{" "}
                <a
                  target="_blank"
                  rel="noreferrer"
                  href="https://formulaire.defenseurdesdroits.fr/"
                >
                  Défenseur des droits
                </a>
              </li>
              <li>
                Contacter{" "}
                <a
                  target="_blank"
                  rel="noreferrer"
                  href="https://www.defenseurdesdroits.fr/saisir/delegues"
                >
                  le délégué du Défenseur des droits dans votre région
                </a>
              </li>
              <li>
                Envoyer un courrier par la poste (gratuit, ne pas mettre de
                timbre) :
                <br />
                Défenseur des droits
                <br />
                Libre réponse 71120 75342 Paris CEDEX 07
              </li>
            </ul>
          </section>

          <hr />

          <footer>
            <p>
              Cette déclaration d'accessibilité a été créée le{" "}
              <span>27 décembre 2023</span> grâce au{" "}
              <a
                target="_blank"
                rel="noreferrer"
                href="https://betagouv.github.io/a11y-generateur-declaration/#create"
              >
                Générateur de Déclaration d'Accessibilité de BetaGouv
              </a>
              .
            </p>
          </footer>
        </Panel>
      </section>
    </Main>
  )
}

export default AccessibilityDeclaration
