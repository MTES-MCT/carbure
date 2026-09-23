-- Replace personal identifiers after restoring a production dump to a non-prod database.
-- Entity names and business data are left unchanged.

UPDATE authtools_user
SET
  email = CONCAT('user', id, '@anonymized.local'),
  name = CONCAT('Utilisateur ', id);

UPDATE entities
SET
  sustainability_officer = CONCAT('Contact ', id),
  sustainability_officer_email = CONCAT('contact', id, '@anonymized.local'),
  sustainability_officer_phone_number = '';
