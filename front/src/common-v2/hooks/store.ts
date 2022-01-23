import { useReducer, useRef } from "react"

export function useStore<S, A extends ActionHandlers<S>>(
  initialState: S,
  actions: A
): [S, ActionCreators<S, A>] {
  const [state, dispatch] = useReducer((state: S, action: Action<S, A>) => {
    const result = actions[action.type](...action.payload)
    const partialState = typeof result === "function" ? result(state) : result
    return { ...state, ...partialState } as S
  }, initialState)

  const boundActions = useRef<ActionCreators<S, A> | undefined>(undefined)

  if (boundActions.current === undefined) {
    const bound: Partial<ActionCreators<S, A>> = {}
    for (const type in actions) {
      bound[type as keyof A] = (...payload) => dispatch({ type, payload })
    }
    boundActions.current = bound as ActionCreators<S, A>
  }

  return [state, boundActions.current!]
}

export interface Action<S, A extends ActionHandlers<S>> {
  type: keyof A
  payload: Parameters<A[keyof A]>
}

export type ActionHandlers<S> = {
  [key: string]: (...args: any) => Partial<S> | ((state: S) => Partial<S>)
}

export type ActionCreators<S, A extends ActionHandlers<S>> = {
  [K in keyof A]: (...args: Parameters<A[K]>) => void
}

export default useStore
