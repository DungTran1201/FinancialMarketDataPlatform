export type RoutePath =
  | '/'
  | '/dashboard'
  | '/data-flow'
  | '/market-analytics'
  | '/data-management'
  | '/ai-workspace'
  | '/administration';

export interface NavItem {
  id: string;
  label: string;
  path: RoutePath;
  icon: string;
  badge?: string;
}

