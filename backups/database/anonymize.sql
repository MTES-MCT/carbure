-- Replace personal identifiers after restoring a production dump to a non-prod database.
-- Entity names and business data are left unchanged.

UPDATE authtools_user
SET
  email = CONCAT('user', id, '@anonymized.local'),
  name = CONCAT('Utilisateur ', id),
  password = "anonymized-password";

UPDATE entities
SET
  sustainability_officer = CONCAT('Contact ', id),
  sustainability_officer_email = CONCAT('contact', id, '@anonymized.local'),
  sustainability_officer_phone_number = '';

UPDATE sites_productionsites
SET
  manager_name = CONCAT('Manager ', site_ptr_id),
  manager_email = CONCAT('manager', site_ptr_id, '@anonymized.local'),
  manager_phone = '';

UPDATE otp_email_emaildevice
SET
  email = CONCAT('user', user_id, '@anonymized.local'),
  name = IF(
    name LIKE 'email_change_%',
    CONCAT('email_change_user', user_id, '@anonymized.local'),
    name
  );

TRUNCATE TABLE django_admin_log;
