import { useReducer, useRef } from "react"

enum ApiStatus {
  Pending = "pending",
  Error = "error",
  Success = "success",
}

export type ApiState<T> = {
  loading: boolean
  error: string | null
  data: T | null
}

type ApiAction<T> =
  | { type: ApiStatus.Pending }
  | { type: ApiStatus.Error; payload: string }
  | { type: ApiStatus.Success; payload: T }

function reducer<T>(state: ApiState<T>, action: ApiAction<T>): ApiState<T> {
  switch (action.type) {
    case ApiStatus.Pending:
      return { ...state, loading: true }
    case ApiStatus.Error:
      return { loading: false, error: action.payload, data: null }
    case ApiStatus.Success:
      return { loading: false, error: null, data: action.payload }
    default:
      return state
  }
}

const initialState = {
  loading: false,
  error: null,
  data: null,
}

type CancelablePromise = Promise<void> & { cancel?: () => void }
type Resolver<T extends any[]> = (...args: T) => CancelablePromise
type ApiReducer<T> = React.Reducer<ApiState<T>, ApiAction<T>>
type ApiHook<T extends any[], U> = [ApiState<U>, Resolver<T>]

function useAPI<T extends any[], U>(
  createPromise: (...args: T) => Promise<U>
): ApiHook<T, U> {
  const resolveRef = useRef<Resolver<T> | null>(null)
  const [state, dispatch] = useReducer<ApiReducer<U>>(reducer, initialState)

  if (resolveRef.current === null) {
    resolveRef.current = (...args: T) => {
      let cancelled = false

      const resolve = async () => {
        if (!cancelled) {
          // signal that the request process started
          dispatch({ type: ApiStatus.Pending })
        }

        try {
          // actually call the api and wait for the response
          const res = await createPromise(...args)

          // dispatch the data if it was a success
          if (!cancelled) {
            dispatch({ type: ApiStatus.Success, payload: res })
          }
        } catch (err) {
          // otherwise save the error
          if (!cancelled) {
            dispatch({ type: ApiStatus.Error, payload: err.message })
          }
        }
      }

      const promise: CancelablePromise = resolve()
      promise.cancel = () => { cancelled = true } // prettier-ignore

      return promise
    }
  }

  return [state, resolveRef.current]
}

export default useAPI
