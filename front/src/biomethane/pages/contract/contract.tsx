import { ContractAmendments } from "./components/contract-amendments/contract-amendments"
import { ContractFiles } from "./components/contract-files"
import { ContractInfos } from "./components/contract-infos"
import { useGetContractInfos } from "./contract.hooks"
import { ErrorTrackedAmendmentTypes } from "./components/tracked-amendment-types"
import { LoaderOverlay } from "common/components/scaffold"
import { AnnualDeclarationAlert } from "biomethane/components/annual-declaration-alert"
import { getContractWatchedFields } from "./api"
import { WatchedFieldsProvider } from "biomethane/providers/watched-fields"
import { ContractAidOrganism } from "./components/contract-aid-organism"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { FormContext, useForm } from "common/components/form2"
import { ContractInfosForm } from "./types"
import { SectionsManagerProvider } from "common/providers/sections-manager.provider"
import { useMissingFields } from "biomethane/components/missing-fields"
import { GitBookProvider, useGitBook } from "@gitbook/embed/react"
import { GitBookFrameClient } from "@gitbook/embed"
import { useEffect, useRef } from "react"

export const BiomethaneContractPageContent = () => {
  const form = useForm<ContractInfosForm>({})
  const { result: contractInfos, loading } = useGetContractInfos({
    onSuccess: (contractInfos) => {
      form.setValue(contractInfos ?? {})
    },
    onError: () => {
      form.setValue({})
    },
  })
  const { hasSelectedEntity } = useSelectedEntity()

  useMissingFields(form)
  useDocumentation("/biomethane/parametres-de-la-societe/contrat")

  if (loading) return <LoaderOverlay />

  return (
    <FormContext.Provider value={form}>
      <WatchedFieldsProvider
        apiFunction={getContractWatchedFields}
        queryKey="contract-watched-fields"
      >
        {!hasSelectedEntity && <AnnualDeclarationAlert />}
        {contractInfos && contractInfos.tracked_amendment_types.length > 0 && (
          <ErrorTrackedAmendmentTypes
            trackedAmendmentTypes={contractInfos.tracked_amendment_types}
          />
        )}
        {(contractInfos || (!contractInfos && !loading)) && (
          <ContractInfos contract={contractInfos} />
        )}
        <ContractFiles contract={contractInfos} />
        <ContractAmendments contract={contractInfos} />
        <ContractAidOrganism contract={contractInfos} />
      </WatchedFieldsProvider>
    </FormContext.Provider>
  )
}

export const BiomethaneContractPage = () => (
  <>
    <GitBookProvider siteURL="https://carbure-1.gitbook.io/">
      <SectionsManagerProvider>
        <BiomethaneContractPageContent />
      </SectionsManagerProvider>
    </GitBookProvider>
  </>
)

function useDocumentation(path: string) {
  const gitbook = useGitBook()
  const iframeRef = useRef<HTMLIFrameElement>()
  const frameRef = useRef<GitBookFrameClient>()

  useEffect(() => {
    const iframe = iframeRef.current ?? document.createElement("iframe")
    iframe.src = gitbook.getFrameURL({})
    iframe.width = "720px"
    iframe.height = "100%"
    iframe.style.border = "1px solid var(--border-default-grey)"
    iframeRef.current = iframe

    const sibling = document.querySelector("#root #app div section")
    sibling?.after(iframe)

    const frame = gitbook.createFrame(iframeRef.current)
    frameRef.current = frame
    frame.configure({ tabs: ["docs"] })

    return () => {
      iframeRef.current?.remove()
    }
  }, [gitbook, path])

  useEffect(() => {
    frameRef.current?.navigateToPage(path)
  }, [path])
}
