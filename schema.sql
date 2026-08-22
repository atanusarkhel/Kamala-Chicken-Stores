-- Run this in Supabase: Project -> SQL Editor -> New Query

create table if not exists business_entries (
    id               bigint generated always as identity primary key,
    entry_date       date not null,
    submitted_by     text not null,
    revenue          numeric not null,
    cost             numeric not null,
    units_sold       integer not null,
    profit           numeric not null,
    margin_pct       numeric not null,
    avg_price_per_unit numeric not null,
    created_at       timestamptz default now()
);

create index if not exists idx_business_entries_date on business_entries (entry_date);
