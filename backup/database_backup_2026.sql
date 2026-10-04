-- =======================================================
-- PRODUCTION DATABASE DUMP (DO NOT EXPOSE TO PUBLIC!)
-- Generated: 2026-10-01 04:30:00 UTC
-- Secret Flag: FLAG{OPEN_DIR_DATABASE_LEAK_9921}
-- =======================================================

CREATE TABLE internal_admin_vault (
    id INT PRIMARY KEY,
    vault_name VARCHAR(100),
    master_key VARCHAR(255)
);

INSERT INTO internal_admin_vault VALUES (1, 'Root_Vault_Alpha', 'KEY_77a98bc01923485720194857');
INSERT INTO internal_admin_vault VALUES (2, 'AWS_KMS_Secondary', 'KEY_992817204918274910293847');

-- User Master Hash
INSERT INTO users VALUES (99, 'super_root', '$2b$12$K8y4r2...internal_hash', 'root@company.local');
