import { useCallback, useReducer } from "react"

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

type CancelablePromise<T> = Promise<T | undefined> & { cancel?: () => void }
type Resolver<T extends any[], U> = (...args: T) => CancelablePromise<U>
type ApiReducer<T> = React.Reducer<ApiState<T>, ApiAction<T>>
type ApiHook<T extends any[], U> = [ApiState<U>, Resolver<T, U>]

function useAPI<T extends any[], U>(
  createPromise: (...args: T) => Promise<U>
): ApiHook<T, U> {
  // const resolveRef = useRef<Resolver<T> | null>(null)
  const [state, dispatch] = useReducer<ApiReducer<U>>(reducer, initialState)

  const resolve = useCallback(
    (...args: T) => {
      let cancelled = false

      // returns true if it was a success, false otherwise
      async function resolve() {
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
            return res
          }
        } catch (err) {
          // otherwise save the error
          if (!cancelled) {
            dispatch({ type: ApiStatus.Error, payload: err.message })
          }
        }
      }

      const promise: CancelablePromise<U> = resolve()
      promise.cancel = () => { cancelled = true } // prettier-ignore

      return promise
    },
    [dispatch, createPromise]
  )

  return [state, resolve]
}

export default useAPI
