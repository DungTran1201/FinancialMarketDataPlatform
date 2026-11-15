export type UserRole = 'ADMIN' | 'ANALYST' | 'OPERATOR' | 'VIEWER';
export type UserTier = 'ANONYMOUS' | 'BASIC' | 'PRO' | 'INSTITUTIONAL';

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  tier: UserTier;
  created_at: string;
  last_login?: string;
}

export interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
  rate_limit_rpm: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in_seconds: number;
}

