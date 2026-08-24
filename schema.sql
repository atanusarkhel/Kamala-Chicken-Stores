-- Run this in Supabase: Project -> SQL Editor -> New Query
-- WARNING: This replaces the old simple business_input / business_metrics
-- tables with the full categorized structure. If you have data in the old
-- tables you want to keep, export it first (Table Editor -> ... -> Export
-- as CSV) before running this.

drop table if exists business_metrics;
drop table if exists business_input;

-- ---------------------------------------------------------------------
-- INPUT TABLE
-- ---------------------------------------------------------------------
create table business_input (
    id            bigint generated always as identity primary key,
    entry_date    date not null unique,
    submitted_by  text not null,

    -- Category: Stock / Ajker Kena
    chandan_quantity_kg        numeric(10,2) default 0,
    chandan_price_per_kg       numeric default 0,
    chandan_payment             numeric default 0,
    sabir_quantity_kg          numeric(10,2) default 0,
    sabir_price_per_kg         numeric default 0,
    sabir_payment               numeric default 0,
    snandi_quantity_kg         numeric(10,2) default 0,
    snandi_price_per_kg        numeric default 0,
    snandi_payment              numeric default 0,
    stock_other1_quantity_kg   numeric(10,2) default 0,
    stock_other1_price_per_kg  numeric default 0,
    stock_other1_payment        numeric default 0,
    stock_other2_quantity_kg   numeric(10,2) default 0,
    stock_other2_price_per_kg  numeric default 0,
    stock_other2_payment        numeric default 0,
    ajke_mal_pore_ache_kg       numeric(10,2) default 0,

    -- Category: Sales / Hindusthan, Other1, Other2 (hotels)
    hotel1_sales_kg       numeric(10,2) default 0,
    hotel1_price_per_kg   numeric default 0,
    hotel1_payment        numeric default 0,
    hotel2_sales_kg       numeric(10,2) default 0,
    hotel2_price_per_kg   numeric default 0,
    hotel2_payment        numeric default 0,
    hotel3_sales_kg       numeric(10,2) default 0,
    hotel3_price_per_kg   numeric default 0,
    hotel3_payment        numeric default 0,

    -- Category: Sales / Dokan
    -- chicken_size stored as numeric: 1 = Small, 2 = Medium, 3 = Big
    chicken_size                  numeric default 2,
    mangso_price_per_kg           numeric default 0,
    gota_customer_sales_kg        numeric(10,2) default 0,
    gota_customer_price_per_kg    numeric default 0,
    gota_dokandar_sales_kg        numeric(10,2) default 0,
    gota_dokandar_price_per_kg    numeric default 0,
    chhat_sales_kg                numeric(10,2) default 0,
    chhat_price_per_kg            numeric default 0,

    -- Category: Cashflow
    total_cash_ache                numeric default 0,
    phonepe_balance                numeric default 0,
    phonepe_aseche                 numeric default 0,
    phonepe_payment_hoyeche        numeric default 0,
    ajker_dokane_dhar_diyeche      numeric default 0,
    ajke_dhar_aday_hoyeche         numeric default 0,
    ajker_advance_payment_aseche   numeric default 0,
    ajke_mangso_pore_ache          numeric default 0,
    murgi_mangso_loss              numeric default 0,

    -- Category: Expense
    emi_box          numeric default 0,
    labour           numeric default 0,
    desi_murgi       numeric default 0,
    murgi_mash       numeric default 0,
    susan_labour     numeric default 0,
    paper            numeric default 0,
    bazar            numeric default 0,
    gari_vara        numeric default 0,
    gas              numeric default 0,
    expense_other1   numeric default 0,
    expense_other2   numeric default 0,
    expense_other3   numeric default 0,
    expense_other4   numeric default 0,
    expense_other5   numeric default 0,

    -- Category: Personal Dhar
    vodu             numeric default 0,
    atanu            numeric default 0,
    personal_other1  numeric default 0,
    personal_other2  numeric default 0,
    personal_other3  numeric default 0,
    personal_other4  numeric default 0,
    personal_other5  numeric default 0,

    created_at timestamptz default now(),
    updated_at timestamptz
);

create index idx_business_input_date on business_input (entry_date);

-- ---------------------------------------------------------------------
-- OUTPUT TABLE — computed aggregates (see note in chat re: formulas)
-- ---------------------------------------------------------------------
create table business_metrics (
    id                        bigint generated always as identity primary key,
    entry_date                date not null,
    submitted_by              text not null,
    input_id                  bigint references business_input (id),

    total_stock_quantity_kg   numeric(10,2) default 0,
    total_stock_cost          numeric default 0,
    total_sales_quantity_kg   numeric(10,2) default 0,
    total_sales_revenue       numeric default 0,
    total_expense             numeric default 0,
    total_personal_dhar       numeric default 0,
    estimated_profit          numeric default 0,

    created_at timestamptz default now(),
    updated_at timestamptz
);

create index idx_business_metrics_date on business_metrics (entry_date);

-- ---------------------------------------------------------------------
-- If you already ran an earlier version of this schema and don't want
-- to drop your data, run just these two lines instead of the whole
-- file above, to add the new updated_at columns:
--
-- alter table business_input add column if not exists updated_at timestamptz;
-- alter table business_metrics add column if not exists updated_at timestamptz;
--
-- If chicken_size already exists as "text" and you need to convert it to
-- numeric (1=Small, 2=Medium, 3=Big) without dropping the table, run:
-- alter table business_input alter column chicken_size type smallint
--   using (case chicken_size
--            when 'Small' then 1
--            when 'Medium' then 2
--            when 'Big' then 3
--            else null
--          end);
