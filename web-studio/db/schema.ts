import { index, integer, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

// Every write appends a complete versioned synthetic workspace. Keeping prior
// versions makes review revocation and human decision history auditable without
// editing old records. Revision uniqueness rejects racing writes.
export const studioSnapshots = sqliteTable("studio_snapshots", {
  seq: integer("seq").primaryKey({ autoIncrement: true }),
  userId: text("user_id").notNull(),
  revision: integer("revision").notNull(),
  action: text("action").notNull(),
  actorId: text("actor_id").notNull(),
  stateJson: text("state_json").notNull(),
  createdAt: text("created_at").notNull(),
}, table => [
  uniqueIndex("studio_snapshots_user_revision_unique").on(table.userId, table.revision),
  index("studio_snapshots_user_latest_idx").on(table.userId, table.revision),
]);
