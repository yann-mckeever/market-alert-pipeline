CREATE TABLE IF NOT EXISTS market_data (
	id SERIAL PRIMARY KEY,
	date TIMESTAMP NOT NULL,
	ticker VARCHAR(10) NOT NULL,
	open_price NUMERIC(12,4),
	close_price NUMERIC(12,4),
	volume BIGINT,
	inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT unique_market_entry UNIQUE (date,ticker)
);

CREATE TABLE IF NOT EXISTS ml_predictions(
	id SERIAL PRIMARY KEY,
	prediction_date TIMESTAMP NOT NULL,
	ticker VARCHAR(10) NOT NULL,
	predicted_value NUMERIC(12,4),
	is_anomaly BOOLEAN NOT NULL,
	anomaly_score NUMERIC(6,4),
	model_version VARCHAR(20) NOT NULL,
	created_at TIMESTAMP DEFAULT TIMESTAMP_CURRENT,
);

CREATE INDEX IF NOT EXISTS idx_market_data_date ON market_data(date);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON ml_predictions(prediction_date);

