CREATE TABLE `studio_snapshots` (
	`seq` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`revision` integer NOT NULL,
	`action` text NOT NULL,
	`actor_id` text NOT NULL,
	`state_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `studio_snapshots_user_revision_unique` ON `studio_snapshots` (`user_id`,`revision`);--> statement-breakpoint
CREATE INDEX `studio_snapshots_user_latest_idx` ON `studio_snapshots` (`user_id`,`revision`);