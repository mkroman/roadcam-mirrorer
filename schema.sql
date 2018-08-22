CREATE TABLE `downloads` (
  `id` INTEGER PRIMARY KEY,
  `thing_id` VARCHAR(15) NOT NULL,
  `url` text NOT NULL,
  `title` text NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `downloaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `path` text
);

CREATE INDEX `idx_download_thing_id` ON downloads(thing_id);
