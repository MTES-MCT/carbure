import { useEffect, useReducer, useState } from "react"
import { ApiPromise } from "../services/api"

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
      return { loading: true, error: null, data: null }
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

type ApiReducer<T> = React.Reducer<ApiState<T>, ApiAction<T>>

type ApiHook<T> = [
  ApiState<T>,
  React.Dispatch<React.SetStateAction<ApiPromise<T> | null>>
]

function useAPI<T>(): ApiHook<T> {
  const [promise, setPromise] = useState<ApiPromise<T> | null>(null)
  const [state, dispatch] = useReducer<ApiReducer<T>>(reducer, initialState)

  useEffect(() => {
    let canceled = false

    async function resolve() {
      // don't run fetch if the promise is not set
      if (!promise) return

      // signal that the request process started
      dispatch({ type: ApiStatus.Pending })

      try {
        // actually call the api and wait for the response
        const res = await promise

        // stop doing anything if this request was canceled
        if (canceled) {
          return
        }

        if (res.status === "success") {
          dispatch({ type: ApiStatus.Success, payload: res.data })
        } else if (res.status === "error" || res.status === "forbidden") {
          dispatch({ type: ApiStatus.Error, payload: res.message })
        }
      } catch (err) {
        dispatch({ type: ApiStatus.Error, payload: err.message })
      }
    }

    resolve()

    // cancel the request if the component is rerendered while the server is working
    return () => {
      canceled = true
    }
  }, [promise]) // restart the process every time the promise changes

  return [state, setPromise]
}

export default useAPI
