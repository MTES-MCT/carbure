import { ReactNode, useMemo } from "react"
import {
  AnnualDeclarationTiruertContext,
  AnnualDeclarationTiruertContextValue,
} from "./annual-declaration-tiruert.provider"

/** Default context value for Storybook when using MockAnnualDeclarationTiruertProvider. */
export const DEFAULT_MOCK_DECLARATION_VALUE: AnnualDeclarationTiruertContextValue =
  {
    currentDeclarationYear: 2025,
    isDeclarationInCurrentPeriod: true,
    selectedYear: 2025,
  }

export interface MockAnnualDeclarationTiruertProviderProps {
  readonly children: ReactNode
  /** Override part or all of the context value (default: DEFAULT_MOCK_DECLARATION_VALUE). */
  readonly value?: Partial<AnnualDeclarationTiruertContextValue>
}

/**
 * Provider pour Storybook : fournit le contexte déclaration annuelle teneur avec des valeurs
 * configurables, sans appel API ni useParams.
 */
export function MockAnnualDeclarationTiruertProvider({
  children,
  value: valueOverride,
}: MockAnnualDeclarationTiruertProviderProps) {
  const value = useMemo<AnnualDeclarationTiruertContextValue>(
    () => ({
      ...DEFAULT_MOCK_DECLARATION_VALUE,
      ...valueOverride,
    }),
    [valueOverride]
  )
  return (
    <AnnualDeclarationTiruertContext.Provider value={value}>
      {children}
    </AnnualDeclarationTiruertContext.Provider>
  )
}
