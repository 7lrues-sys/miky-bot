-- File-level: Initial SQL schema for Mikky bot (PostgreSQL)
-- Creates core tables required by the backend MVP.

CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  language VARCHAR(16) DEFAULT 'en',
  timezone VARCHAR(64),
  terms_accepted BOOLEAN DEFAULT FALSE,
  accepted_at TIMESTAMP WITH TIME ZONE,
  subscription_status VARCHAR(32) DEFAULT 'free',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  task_text TEXT NOT NULL,
  deadline TIMESTAMP WITH TIME ZONE,
  status VARCHAR(16) DEFAULT 'active',
  location_query TEXT,
  location_raw TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_reminded_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  text_default TEXT NOT NULL,
  is_golden BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_predictions (
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  prediction_id BIGINT NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
  date_sent DATE NOT NULL,
  PRIMARY KEY (user_id, prediction_id)
);

CREATE TABLE IF NOT EXISTS daily_push_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date_sent DATE NOT NULL,
  push_type VARCHAR(32) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE (user_id, date_sent, push_type)
);

CREATE TABLE IF NOT EXISTS payment_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  amount NUMERIC,
  currency VARCHAR(8),
  status VARCHAR(16),
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  package_type VARCHAR(32),
  start_date TIMESTAMP WITH TIME ZONE,
  end_date TIMESTAMP WITH TIME ZONE,
  auto_renew BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  payment_log_id BIGINT REFERENCES payment_logs(id),
  gateway VARCHAR(64),
  webhook_status VARCHAR(32),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_insights (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category VARCHAR(128),
  fact TEXT,
  status VARCHAR(32) DEFAULT 'unresolved',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_history (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(16),
  content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS media_archive (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_id TEXT,
  status VARCHAR(32) DEFAULT 'unrecognized',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
