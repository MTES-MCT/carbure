import React from "react";
import pt from "path";

import {
  Route as BaseRoute,
  Link as BaseLink,
  NavLink as BaseNavLink,
  Redirect as BaseRedirect,
  Switch as BaseSwitch,
  matchPath,
  useHistory,
  useRouteMatch,
  RouteProps,
  LinkProps,
  NavLinkProps,
  RedirectProps,
  SwitchProps,
  useLocation,
} from "react-router-dom";

function isAbsolute(path: any) {
  if (!path) return false;
  else if (typeof path === "string") return path.startsWith("/");
  else return true;
}

export function combine(root: string, path: any) {
  if (isAbsolute(path)) return path;
  else if (typeof path === "string") return pt.join(root, path);
  else return path;
}

export function useNavigate() {
  const history = useHistory();
  const match = useRouteMatch();
  const location = useLocation();

  return (to: string) => history.push(combine(match.url, to + location.search));
}

export function useMatcher() {
  const location = useLocation();
  const routeMatch = useRouteMatch();

  return (path: string | undefined) => {
    if (path === undefined) return null;
    const fullPath = combine(routeMatch.url, path);
    return matchPath(location.pathname + location.hash, {
      path: fullPath,
      exact: path === "/",
    });
  };
}

export const Route = ({ path, ...props }: RouteProps) => {
  const match = useRouteMatch();
  return <BaseRoute {...props} path={combine(match.path, path)} />;
};

export const Link = ({ to, ...props }: Partial<LinkProps>) => {
  const match = useRouteMatch();
  return <BaseLink {...props} to={combine(match.url, to)} />;
};

export type RelNavLinkProps = NavLinkProps;

export const NavLink = ({ to, ...props }: RelNavLinkProps) => {
  const match = useRouteMatch();
  return <BaseNavLink {...props} to={combine(match.url, to)} />;
};

export const Redirect = ({ from, to, ...props }: RedirectProps) => {
  const match = useRouteMatch();
  const baseFrom = combine(match.url, from);
  const baseTo = combine(match.url, to);
  return <BaseRedirect {...props} from={baseFrom} to={baseTo} />;
};

// the basic Switch component from react-router only works with basic react-router Route component
// this component tricks it into working with the custom routing components of this file
export const Routes = ({ children }: SwitchProps) => {
  const match = useRouteMatch();

  return (
    <BaseSwitch>
      {React.Children.map(children, (child: any) => {
        const isRoute = child?.type === Route;
        const isRedirect = child?.type === Redirect;

        const path = child?.props?.path;
        const to = child?.props?.to;
        const from = child?.props?.from;

        // relative route child, create equivalent base route
        if (isRoute && !isAbsolute(path)) {
          const basePath = combine(match.path, path);
          return <BaseRoute {...child.props} path={basePath} />;
        }
        // relative redirect child, create equivalent base redirect
        else if (isRedirect && (!isAbsolute(from) || !isAbsolute(to))) {
          const baseFrom = combine(match.url, from);
          const baseTo = combine(match.url, to);
          return <BaseRedirect {...child.props} from={baseFrom} to={baseTo} />;
        }
        // otherwise return the child as is
        else {
          return child;
        }
      })}
    </BaseSwitch>
  );
};
