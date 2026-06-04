# Gestion des requêtes (React Query)

Carbure migre progressivement de `react-async-hook` (`common/hooks/async`) vers **TanStack React Query** (`common/hooks/async-rq`).

Les deux systèmes coexistent temporairement. **Ne pas les mélanger dans un même flux query/mutation** sans raison (invalidations croisées, états incohérents).

## Quand utiliser quoi ?

| Hook | Import | Usage |
|------|--------|-------|
| Nouveau code migré | `common/hooks/async-rq` | Queries et mutations React Query |
| Code legacy | `common/hooks/async` | Tout ce qui n'a pas encore été migré |

Provider global : `QueryClientProvider` dans `src/index.tsx`, configuré via `common/hooks/query-client.ts`.

## Queries

```typescript
import { useQuery } from "common/hooks/async-rq"
import { COMMON_QUERY_KEYS } from "common/hooks/async-rq"
import * as api from "common/api"

const settings = useQuery({
  queryKey: COMMON_QUERY_KEYS.userSettings,
  queryFn: api.getUserSettings,
})
```

### Correspondance avec l'ancien hook

| Legacy (`async`) | React Query (`async-rq`) |
|------------------|--------------------------|
| `result` | `data` |
| `loading` | `isPending` |
| `execute(...params)` | `refetch()` ou `queryKey` paramétrée |
| `{ key, params }` | `{ queryKey: [key, ...params], queryFn }` |

Pour une query paramétrée, inclure les paramètres dans la clé :

```typescript
useQuery({
  queryKey: ["entity-rights", entityId],
  queryFn: () => api.getEntityRights(entityId),
})
```

## Mutations

Comme le legacy `async` : **`useMutation(apiFn, options)`** avec `invalidates` en plus des options React Query. Pas de `mutationFn` à écrire.

Les variables passées à `mutate` / `mutateAsync` sont le tuple **`Parameters<typeof apiFn>`**.

```typescript
import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
import * as api from "../api"

const requestAccess = useMutation(api.requestAccess, {
  invalidates: [COMMON_QUERY_KEYS.userSettings],
  onSuccess: () => notify(t("Enregistré"), { variant: "success" }),
})

// Plusieurs args API → tuple
await requestAccess.mutateAsync([entityId, role])

// Un seul arg API → tuple à un élément
await revokeMyself.mutateAsync([entityId])

// Aucun arg API → mutate() sans variable
logoutMutation.mutate()

// Args fixés dans le hook (entity.id, etc.)
const toggleMAC = useMutation(
  (toggle: boolean) => api.toggleMAC(entity.id, toggle),
  { invalidates: [COMMON_QUERY_KEYS.userSettings] }
)
toggleMAC.mutate([true])
```

| Legacy (`async`) | React Query (`async-rq`) |
|------------------|--------------------------|
| `useMutation(apiFn, opts)` | `useMutation(apiFn, opts)` |
| `execute(...args)` | `mutateAsync([...args])` |
| `loading` | `isPending` |

## Query keys

### Clés transverses (`COMMON_QUERY_KEYS`)

Les queries utilisées par plusieurs modules sont exportées depuis `async-rq.ts` :

```typescript
export const COMMON_QUERY_KEYS = {
  userSettings: ["user-settings"] as const,
}
```

Les clés propres à un module vivent à la racine du module (ex. `settings/query-keys.ts`), avec les mêmes noms que le legacy quand c'est possible.

## Migration d'un domaine

Checklist par slice (ex. settings, auth, biométhane…) :

1. Migrer la ou les `useQuery` → `async-rq` (`queryKey` + `queryFn`).
2. Migrer les `useMutation` : `useMutation(apiFn, { invalidates, ... })`.
3. Remplacer les strings magiques par des query keys exportées.
4. Vérifier les invalidations croisées depuis d'autres modules.
5. Supprimer les imports `common/hooks/async` du fichier migré.
6. Tester manuellement : lecture, création, modification, suppression, navigation.

### Exemples déjà migrés

- Query : `common/hooks/user.ts` (`user-settings`)
- Mutations : auth (logout, OTP), account (droits, email), settings (company-info, company-options, certificat par défaut), registration, contract-infos (biomethane)

### Cas mixte temporaire

Tant qu'une page n'est pas entièrement migrée, on peut garder les deux imports avec un alias explicite :

```typescript
import { useQuery, useMutation as useLegacyMutation } from "common/hooks/async"
import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"
```

Éviter de laisser ce pattern durablement : migrer le reste de la page dès que possible.

## Configuration par défaut

`query-client.ts` :

- `staleTime` : 60 s
- `retry` : 1 (queries), 0 (mutations)
- `refetchOnWindowFocus` : false
