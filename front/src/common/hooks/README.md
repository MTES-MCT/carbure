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

Le wrapper `useMutation` de `async-rq` reprend l'option `invalidates` pour rafraîchir automatiquement les queries après succès.

```typescript
import { COMMON_QUERY_KEYS, useMutation } from "common/hooks/async-rq"

const updateEntity = useMutation({
  mutationFn: (payload) => api.updateEntity(entity.id, payload),
  invalidates: [COMMON_QUERY_KEYS.userSettings],
  onSuccess: () => notify(t("Enregistré"), { variant: "success" }),
})

// Déclenchement
updateEntity.mutate(payload)
// ou
await updateEntity.mutateAsync(payload)
```

| Legacy (`async`) | React Query (`async-rq`) |
|------------------|--------------------------|
| `execute(...args)` | `mutate(...args)` ou `mutateAsync(...args)` |
| `loading` | `isPending` |

## Query keys

### Clés transverses (`COMMON_QUERY_KEYS`)

Les queries utilisées par plusieurs modules sont exportées depuis `async-rq.ts` :

```typescript
export const COMMON_QUERY_KEYS = {
  userSettings: ["user-settings"] as const,
}
```


## Migration d'un domaine

Checklist par slice (ex. settings, auth, biométhane…) :

1. Migrer la ou les `useQuery` → `async-rq` (`queryKey` + `queryFn`).
2. Migrer les `useMutation` associées.
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
