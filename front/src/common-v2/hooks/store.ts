import { useReducer, useRef } from "react"

export function useStore<S, A extends ActionHandlers>(
  initialState: S,
  actions: A
): [S, ActionCreators<A>] {
  const [state, dispatch] = useReducer(
    (state: S, action: Action<A>) => ({
      ...state,
      ...actions[action.type](...action.payload),
    }),
    initialState
  )

  const boundActions = useRef<ActionCreators<A> | undefined>(undefined)

  if (boundActions.current === undefined) {
    const bound: Partial<ActionCreators<A>> = {}
    for (const type in actions) {
      bound[type as keyof A] = (...payload) => dispatch({ type, payload })
    }
    boundActions.current = bound as ActionCreators<A>
  }

  return [state, boundActions.current!]
}

export interface Action<A extends ActionHandlers> {
  type: keyof A
  payload: Parameters<A[keyof A]>
}

export type ActionHandlers = {
  [key: string]: (...args: any) => any
}

export type ActionCreators<A extends ActionHandlers> = {
  [K in keyof A]: (...args: Parameters<A[K]>) => void
}

export default useStore