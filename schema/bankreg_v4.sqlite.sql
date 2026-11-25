-- BankRegSQL V2 public SQLite schema.
-- Generated from the EAST-independent canonical specification.
-- SQLite 3.38+; comments and source mappings are intentionally external.
PRAGMA foreign_keys = ON;

CREATE TABLE institution (
    institution_id TEXT NOT NULL,
    institution_name TEXT NOT NULL,
    institution_type TEXT NOT NULL,
    country_code TEXT NOT NULL,
    region_code TEXT,
    established_on TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_institution_country_code CHECK (length(country_code) = 2 AND country_code = upper(country_code) AND country_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_institution PRIMARY KEY (institution_id)
) STRICT;

CREATE TABLE organization_unit (
    org_unit_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    parent_org_unit_id TEXT,
    unit_name TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    region_code TEXT,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_credit_facility_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_organization_unit_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_organization_unit PRIMARY KEY (org_unit_id),
    CONSTRAINT ck_organization_unit_table_1 CHECK (parent_org_unit_id IS NULL OR parent_org_unit_id <> org_unit_id),
    CONSTRAINT fk_organization_unit_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_organization_unit_parent_org_unit_id FOREIGN KEY (parent_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE staff_member (
    staff_id TEXT NOT NULL,
    person_party_id TEXT NOT NULL UNIQUE,
    home_org_unit_id TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    hired_on TEXT,
    departed_on TEXT,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_staff_member_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_staff_member_departed_on CHECK (departed_on IS NULL OR hired_on IS NULL OR departed_on >= hired_on),
    CONSTRAINT pk_staff_member PRIMARY KEY (staff_id),
    CONSTRAINT fk_staff_member_person_party_id FOREIGN KEY (person_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_staff_member_home_org_unit_id FOREIGN KEY (home_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE staff_assignment (
    assignment_id TEXT NOT NULL,
    staff_id TEXT NOT NULL,
    org_unit_id TEXT NOT NULL,
    role_code TEXT NOT NULL,
    role_title TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_staff_assignment_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_staff_assignment PRIMARY KEY (assignment_id),
    CONSTRAINT fk_staff_assignment_staff_id FOREIGN KEY (staff_id) REFERENCES staff_member (staff_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_staff_assignment_org_unit_id FOREIGN KEY (org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE service_operator (
    operator_id TEXT NOT NULL,
    staff_id TEXT,
    org_unit_id TEXT NOT NULL,
    operator_kind TEXT NOT NULL,
    authority_level TEXT,
    activated_on TEXT,
    deactivated_on TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_service_operator_deactivated_on CHECK (deactivated_on IS NULL OR activated_on IS NULL OR deactivated_on >= activated_on),
    CONSTRAINT pk_service_operator PRIMARY KEY (operator_id),
    CONSTRAINT fk_service_operator_staff_id FOREIGN KEY (staff_id) REFERENCES staff_member (staff_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_service_operator_org_unit_id FOREIGN KEY (org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE party (
    party_id TEXT NOT NULL,
    party_type TEXT NOT NULL,
    display_name TEXT NOT NULL,
    customer_segment TEXT,
    home_org_unit_id TEXT,
    onboarded_on TEXT,
    status TEXT NOT NULL,
    CONSTRAINT pk_party PRIMARY KEY (party_id),
    CONSTRAINT fk_party_home_org_unit_id FOREIGN KEY (home_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE person_profile (
    party_id TEXT NOT NULL,
    occupation_code TEXT,
    employment_sector TEXT,
    employer_party_id TEXT,
    annual_income REAL,
    is_public_official INTEGER NOT NULL,
    CONSTRAINT ck_person_profile_annual_income CHECK (annual_income IS NULL OR annual_income >= 0),
    CONSTRAINT pk_person_profile PRIMARY KEY (party_id),
    CONSTRAINT fk_person_profile_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_person_profile_employer_party_id FOREIGN KEY (employer_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE industry_sector (
    sector_code TEXT NOT NULL,
    sector_name_zh TEXT NOT NULL,
    sector_name_en TEXT NOT NULL,
    parent_sector_code TEXT,
    risk_category TEXT,
    CONSTRAINT pk_industry_sector PRIMARY KEY (sector_code),
    CONSTRAINT fk_industry_sector_parent_sector_code FOREIGN KEY (parent_sector_code) REFERENCES industry_sector (sector_code) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE organization_profile (
    party_id TEXT NOT NULL,
    legal_form TEXT,
    organization_kind TEXT,
    industry_code TEXT,
    business_scope TEXT,
    registered_region TEXT,
    registration_expires_on TEXT,
    legal_representative_party_id TEXT,
    operating_status TEXT,
    CONSTRAINT pk_organization_profile PRIMARY KEY (party_id),
    CONSTRAINT fk_organization_profile_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_organization_profile_industry_code FOREIGN KEY (industry_code) REFERENCES industry_sector (sector_code) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_organization_profile_legal_representative_party_id FOREIGN KEY (legal_representative_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE party_relation (
    relation_id TEXT NOT NULL,
    source_party_id TEXT NOT NULL,
    target_party_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    confidence_level TEXT,
    source_kind TEXT NOT NULL,
    CONSTRAINT ck_party_relation_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_party_relation PRIMARY KEY (relation_id),
    CONSTRAINT ck_party_relation_table_1 CHECK (source_party_id <> target_party_id),
    CONSTRAINT fk_party_relation_source_party_id FOREIGN KEY (source_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_party_relation_target_party_id FOREIGN KEY (target_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE ownership_interest (
    ownership_id TEXT NOT NULL,
    owner_party_id TEXT NOT NULL,
    target_party_id TEXT NOT NULL,
    ownership_ratio REAL,
    voting_ratio REAL,
    is_controller INTEGER NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_ownership_interest_ownership_ratio CHECK (ownership_ratio >= 0),
    CONSTRAINT ck_ownership_interest_voting_ratio CHECK (voting_ratio >= 0),
    CONSTRAINT ck_ownership_interest_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_ownership_interest PRIMARY KEY (ownership_id),
    CONSTRAINT ck_ownership_interest_table_1 CHECK (owner_party_id <> target_party_id),
    CONSTRAINT ck_ownership_interest_table_2 CHECK (ownership_ratio IS NULL OR ownership_ratio <= 1),
    CONSTRAINT ck_ownership_interest_table_3 CHECK (voting_ratio IS NULL OR voting_ratio <= 1),
    CONSTRAINT fk_ownership_interest_owner_party_id FOREIGN KEY (owner_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_ownership_interest_target_party_id FOREIGN KEY (target_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE group_membership (
    membership_id TEXT NOT NULL,
    group_party_id TEXT NOT NULL,
    member_party_id TEXT NOT NULL,
    membership_type TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_group_membership_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_group_membership PRIMARY KEY (membership_id),
    CONSTRAINT ck_group_membership_table_1 CHECK (group_party_id <> member_party_id),
    CONSTRAINT fk_group_membership_group_party_id FOREIGN KEY (group_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_group_membership_member_party_id FOREIGN KEY (member_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE financial_snapshot (
    financial_snapshot_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    total_assets REAL,
    total_liabilities REAL,
    net_assets REAL,
    annual_revenue REAL,
    source_kind TEXT NOT NULL,
    CONSTRAINT ck_financial_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_financial_snapshot_total_assets CHECK (total_assets >= 0),
    CONSTRAINT ck_financial_snapshot_total_liabilities CHECK (total_liabilities >= 0),
    CONSTRAINT ck_financial_snapshot_annual_revenue CHECK (annual_revenue >= 0),
    CONSTRAINT pk_financial_snapshot PRIMARY KEY (financial_snapshot_id),
    CONSTRAINT fk_financial_snapshot_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE account (
    account_id TEXT NOT NULL,
    institution_id TEXT,
    org_unit_id TEXT,
    account_kind TEXT NOT NULL,
    account_subtype TEXT,
    currency_code TEXT NOT NULL,
    opened_on TEXT,
    closed_on TEXT,
    last_activity_on TEXT,
    is_external INTEGER NOT NULL,
    status TEXT NOT NULL,
    CONSTRAINT ck_account_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_account_closed_on CHECK (closed_on IS NULL OR opened_on IS NULL OR closed_on >= opened_on),
    CONSTRAINT pk_account PRIMARY KEY (account_id),
    CONSTRAINT fk_account_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_account_org_unit_id FOREIGN KEY (org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE account_holder (
    account_holder_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    holder_role TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_account_holder_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_account_holder PRIMARY KEY (account_holder_id),
    CONSTRAINT uq_account_holder_1 UNIQUE (account_id, party_id, effective_from),
    CONSTRAINT fk_account_holder_account_id FOREIGN KEY (account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_account_holder_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE account_balance_snapshot (
    account_balance_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    ledger_balance REAL NOT NULL,
    available_balance REAL,
    debit_balance REAL,
    credit_balance REAL,
    CONSTRAINT ck_account_balance_snapshot_debit_balance CHECK (debit_balance IS NULL OR debit_balance >= 0),
    CONSTRAINT ck_account_balance_snapshot_credit_balance CHECK (credit_balance IS NULL OR credit_balance >= 0),
    CONSTRAINT pk_account_balance_snapshot PRIMARY KEY (account_balance_id),
    CONSTRAINT uq_account_balance_snapshot_1 UNIQUE (account_id, as_of_date),
    CONSTRAINT fk_account_balance_snapshot_account_id FOREIGN KEY (account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE payment_event (
    payment_id TEXT NOT NULL,
    from_account_id TEXT,
    to_account_id TEXT,
    business_date TEXT NOT NULL,
    event_time TEXT NOT NULL,
    amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    payment_type TEXT NOT NULL,
    channel TEXT,
    is_cash INTEGER NOT NULL,
    memo TEXT,
    operator_id TEXT,
    origin_org_unit_id TEXT,
    balance_after REAL,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_payment_event_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_payment_event_amount CHECK (amount >= 0),
    CONSTRAINT ck_payment_event_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_payment_event PRIMARY KEY (payment_id),
    CONSTRAINT ck_payment_event_table_1 CHECK (from_account_id IS NULL OR to_account_id IS NULL OR from_account_id <> to_account_id),
    CONSTRAINT ck_payment_event_table_2 CHECK ((is_cash AND (CASE WHEN from_account_id IS NULL THEN 0 ELSE 1 END + CASE WHEN to_account_id IS NULL THEN 0 ELSE 1 END) = 1) OR (NOT is_cash AND from_account_id IS NOT NULL AND to_account_id IS NOT NULL)),
    CONSTRAINT fk_payment_event_from_account_id FOREIGN KEY (from_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_event_to_account_id FOREIGN KEY (to_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_event_operator_id FOREIGN KEY (operator_id) REFERENCES service_operator (operator_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_event_origin_org_unit_id FOREIGN KEY (origin_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE term_deposit (
    account_id TEXT NOT NULL,
    opening_principal REAL NOT NULL,
    booked_on TEXT NOT NULL,
    maturity_on TEXT,
    annual_interest_rate REAL,
    CONSTRAINT ck_term_deposit_opening_principal CHECK (opening_principal >= 0),
    CONSTRAINT ck_term_deposit_maturity_on CHECK (maturity_on IS NULL OR maturity_on >= booked_on),
    CONSTRAINT ck_term_deposit_annual_interest_rate CHECK (annual_interest_rate >= 0),
    CONSTRAINT pk_term_deposit PRIMARY KEY (account_id),
    CONSTRAINT fk_term_deposit_account_id FOREIGN KEY (account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE payment_card (
    card_id TEXT NOT NULL,
    settlement_account_id TEXT NOT NULL,
    holder_party_id TEXT NOT NULL,
    card_type TEXT NOT NULL,
    issued_on TEXT,
    expires_on TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_payment_card_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_payment_card_expires_on CHECK (expires_on IS NULL OR issued_on IS NULL OR expires_on >= issued_on),
    CONSTRAINT pk_payment_card PRIMARY KEY (card_id),
    CONSTRAINT fk_payment_card_settlement_account_id FOREIGN KEY (settlement_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_card_holder_party_id FOREIGN KEY (holder_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE credit_facility (
    facility_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    obligor_party_id TEXT NOT NULL,
    facility_type TEXT NOT NULL,
    limit_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    approved_on TEXT,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_credit_facility_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_credit_facility_limit_amount CHECK (limit_amount >= 0),
    CONSTRAINT ck_credit_facility_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_credit_facility_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_credit_facility PRIMARY KEY (facility_id),
    CONSTRAINT fk_credit_facility_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_facility_obligor_party_id FOREIGN KEY (obligor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE credit_agreement (
    agreement_id TEXT NOT NULL,
    facility_id TEXT,
    institution_id TEXT NOT NULL,
    borrower_party_id TEXT NOT NULL,
    managing_org_unit_id TEXT,
    product_family TEXT NOT NULL,
    purpose_text TEXT,
    target_industry_code TEXT,
    contract_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    signed_on TEXT,
    effective_from TEXT NOT NULL,
    maturity_on TEXT,
    interest_basis TEXT,
    annual_interest_rate REAL,
    rate_spread REAL,
    payment_mode TEXT,
    security_type TEXT,
    business_context_token TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_credit_agreement_contract_amount CHECK (contract_amount >= 0),
    CONSTRAINT ck_credit_agreement_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_credit_agreement_maturity_on CHECK (maturity_on IS NULL OR maturity_on >= effective_from),
    CONSTRAINT ck_credit_agreement_annual_interest_rate CHECK (annual_interest_rate >= 0),
    CONSTRAINT pk_credit_agreement PRIMARY KEY (agreement_id),
    CONSTRAINT fk_credit_agreement_facility_id FOREIGN KEY (facility_id) REFERENCES credit_facility (facility_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_agreement_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_agreement_borrower_party_id FOREIGN KEY (borrower_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_agreement_managing_org_unit_id FOREIGN KEY (managing_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_agreement_target_industry_code FOREIGN KEY (target_industry_code) REFERENCES industry_sector (sector_code) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE credit_participant (
    participant_id TEXT NOT NULL,
    agreement_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    participant_role TEXT NOT NULL,
    commitment_amount REAL,
    participation_ratio REAL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_credit_participant_commitment_amount CHECK (commitment_amount >= 0),
    CONSTRAINT ck_credit_participant_participation_ratio CHECK (participation_ratio >= 0),
    CONSTRAINT ck_credit_participant_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_credit_participant PRIMARY KEY (participant_id),
    CONSTRAINT uq_credit_participant_1 UNIQUE (agreement_id, party_id, participant_role, effective_from),
    CONSTRAINT ck_credit_participant_table_1 CHECK (participation_ratio IS NULL OR participation_ratio <= 1),
    CONSTRAINT fk_credit_participant_agreement_id FOREIGN KEY (agreement_id) REFERENCES credit_agreement (agreement_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_credit_participant_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE loan_drawdown (
    loan_id TEXT NOT NULL,
    agreement_id TEXT NOT NULL,
    loan_account_id TEXT NOT NULL,
    disbursement_account_id TEXT,
    repayment_account_id TEXT,
    disbursed_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    disbursed_on TEXT NOT NULL,
    original_maturity_on TEXT NOT NULL,
    current_maturity_on TEXT NOT NULL,
    closed_on TEXT,
    drawdown_type TEXT NOT NULL,
    payment_mode TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_loan_drawdown_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_loan_drawdown_disbursed_amount CHECK (disbursed_amount >= 0),
    CONSTRAINT ck_loan_drawdown_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_loan_drawdown_original_maturity_on CHECK (original_maturity_on >= disbursed_on),
    CONSTRAINT ck_loan_drawdown_current_maturity_on CHECK (current_maturity_on >= disbursed_on),
    CONSTRAINT ck_loan_drawdown_closed_on CHECK (closed_on IS NULL OR closed_on >= disbursed_on),
    CONSTRAINT pk_loan_drawdown PRIMARY KEY (loan_id),
    CONSTRAINT fk_loan_drawdown_agreement_id FOREIGN KEY (agreement_id) REFERENCES credit_agreement (agreement_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_loan_drawdown_loan_account_id FOREIGN KEY (loan_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_loan_drawdown_disbursement_account_id FOREIGN KEY (disbursement_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_loan_drawdown_repayment_account_id FOREIGN KEY (repayment_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE loan_balance_snapshot (
    loan_balance_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    principal_balance REAL NOT NULL,
    overdue_principal REAL,
    on_balance_interest_arrears REAL,
    off_balance_interest_arrears REAL,
    overdue_since TEXT,
    CONSTRAINT ck_loan_balance_snapshot_principal_balance CHECK (principal_balance >= 0),
    CONSTRAINT ck_loan_balance_snapshot_overdue_principal CHECK (overdue_principal >= 0),
    CONSTRAINT ck_loan_balance_snapshot_on_balance_interest_arrears CHECK (on_balance_interest_arrears >= 0),
    CONSTRAINT ck_loan_balance_snapshot_off_balance_interest_arrears CHECK (off_balance_interest_arrears >= 0),
    CONSTRAINT pk_loan_balance_snapshot PRIMARY KEY (loan_balance_id),
    CONSTRAINT uq_loan_balance_snapshot_1 UNIQUE (loan_id, as_of_date),
    CONSTRAINT fk_loan_balance_snapshot_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE loan_cashflow (
    loan_cashflow_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    payment_id TEXT,
    cashflow_type TEXT NOT NULL,
    business_date TEXT NOT NULL,
    amount REAL NOT NULL,
    principal_balance_after REAL,
    CONSTRAINT ck_loan_cashflow_amount CHECK (amount >= 0),
    CONSTRAINT ck_loan_cashflow_principal_balance_after CHECK (principal_balance_after IS NULL OR principal_balance_after >= 0),
    CONSTRAINT pk_loan_cashflow PRIMARY KEY (loan_cashflow_id),
    CONSTRAINT fk_loan_cashflow_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_loan_cashflow_payment_id FOREIGN KEY (payment_id) REFERENCES payment_event (payment_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE repayment_schedule (
    installment_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    installment_no INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    principal_due REAL NOT NULL,
    interest_due REAL NOT NULL,
    paid_on TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_repayment_schedule_installment_no CHECK (installment_no > 0),
    CONSTRAINT ck_repayment_schedule_principal_due CHECK (principal_due >= 0),
    CONSTRAINT ck_repayment_schedule_interest_due CHECK (interest_due >= 0),
    CONSTRAINT pk_repayment_schedule PRIMARY KEY (installment_id),
    CONSTRAINT uq_repayment_schedule_1 UNIQUE (loan_id, installment_no),
    CONSTRAINT fk_repayment_schedule_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE payment_instruction (
    instruction_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    payment_mode TEXT NOT NULL,
    intended_payee_party_id TEXT,
    intended_payee_account_id TEXT,
    instruction_date TEXT NOT NULL,
    instruction_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_payment_instruction_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_payment_instruction_instruction_amount CHECK (instruction_amount >= 0),
    CONSTRAINT ck_payment_instruction_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_payment_instruction PRIMARY KEY (instruction_id),
    CONSTRAINT fk_payment_instruction_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_instruction_intended_payee_party_id FOREIGN KEY (intended_payee_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_payment_instruction_intended_payee_account_id FOREIGN KEY (intended_payee_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE loan_lineage (
    lineage_id TEXT NOT NULL,
    predecessor_loan_id TEXT NOT NULL,
    successor_loan_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    linked_on TEXT NOT NULL,
    rationale TEXT,
    CONSTRAINT pk_loan_lineage PRIMARY KEY (lineage_id),
    CONSTRAINT ck_loan_lineage_table_1 CHECK (predecessor_loan_id <> successor_loan_id),
    CONSTRAINT fk_loan_lineage_predecessor_loan_id FOREIGN KEY (predecessor_loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_loan_lineage_successor_loan_id FOREIGN KEY (successor_loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE security_agreement (
    security_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    security_type TEXT NOT NULL,
    secured_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    manager_staff_id TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_security_agreement_secured_amount CHECK (secured_amount >= 0),
    CONSTRAINT ck_security_agreement_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_security_agreement_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_security_agreement PRIMARY KEY (security_id),
    CONSTRAINT fk_security_agreement_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_security_agreement_manager_staff_id FOREIGN KEY (manager_staff_id) REFERENCES staff_member (staff_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE secured_obligation (
    secured_obligation_id TEXT NOT NULL,
    security_id TEXT NOT NULL,
    agreement_id TEXT,
    instrument_id TEXT,
    covered_amount REAL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_secured_obligation_covered_amount CHECK (covered_amount >= 0),
    CONSTRAINT ck_secured_obligation_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_secured_obligation PRIMARY KEY (secured_obligation_id),
    CONSTRAINT ck_secured_obligation_table_1 CHECK ((CASE WHEN agreement_id IS NULL THEN 0 ELSE 1 END + CASE WHEN instrument_id IS NULL THEN 0 ELSE 1 END) = 1),
    CONSTRAINT fk_secured_obligation_security_id FOREIGN KEY (security_id) REFERENCES security_agreement (security_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_secured_obligation_agreement_id FOREIGN KEY (agreement_id) REFERENCES credit_agreement (agreement_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_secured_obligation_instrument_id FOREIGN KEY (instrument_id) REFERENCES financial_instrument (instrument_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE guarantor_commitment (
    commitment_id TEXT NOT NULL,
    security_id TEXT NOT NULL,
    guarantor_party_id TEXT NOT NULL,
    guaranteed_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_credit_facility_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_guarantor_commitment_guaranteed_amount CHECK (guaranteed_amount >= 0),
    CONSTRAINT ck_guarantor_commitment_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_guarantor_commitment_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_guarantor_commitment PRIMARY KEY (commitment_id),
    CONSTRAINT fk_guarantor_commitment_security_id FOREIGN KEY (security_id) REFERENCES security_agreement (security_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_guarantor_commitment_guarantor_party_id FOREIGN KEY (guarantor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE collateral_asset (
    collateral_id TEXT NOT NULL,
    owner_party_id TEXT NOT NULL,
    collateral_type TEXT NOT NULL,
    asset_label TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    status TEXT NOT NULL,
    CONSTRAINT ck_collateral_asset_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_collateral_asset PRIMARY KEY (collateral_id),
    CONSTRAINT fk_collateral_asset_owner_party_id FOREIGN KEY (owner_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE collateral_link (
    collateral_link_id TEXT NOT NULL,
    security_id TEXT NOT NULL,
    collateral_id TEXT NOT NULL,
    pledged_amount REAL,
    pledge_ratio REAL,
    lien_priority INTEGER,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_credit_facility_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_collateral_link_pledged_amount CHECK (pledged_amount >= 0),
    CONSTRAINT ck_collateral_link_pledge_ratio CHECK (pledge_ratio >= 0),
    CONSTRAINT ck_collateral_link_lien_priority CHECK (lien_priority IS NULL OR lien_priority > 0),
    CONSTRAINT ck_collateral_link_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_collateral_link PRIMARY KEY (collateral_link_id),
    CONSTRAINT ck_collateral_link_table_1 CHECK (pledge_ratio IS NULL OR pledge_ratio <= 1),
    CONSTRAINT fk_collateral_link_security_id FOREIGN KEY (security_id) REFERENCES security_agreement (security_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_collateral_link_collateral_id FOREIGN KEY (collateral_id) REFERENCES collateral_asset (collateral_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE collateral_valuation (
    valuation_id TEXT NOT NULL,
    collateral_id TEXT NOT NULL,
    valued_on TEXT NOT NULL,
    valuation_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    valuation_type TEXT,
    appraiser_kind TEXT,
    valid_until TEXT,
    CONSTRAINT ck_collateral_valuation_valuation_amount CHECK (valuation_amount >= 0),
    CONSTRAINT ck_collateral_valuation_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_collateral_valuation_valid_until CHECK (valid_until IS NULL OR valid_until >= valued_on),
    CONSTRAINT pk_collateral_valuation PRIMARY KEY (valuation_id),
    CONSTRAINT fk_collateral_valuation_collateral_id FOREIGN KEY (collateral_id) REFERENCES collateral_asset (collateral_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE capital_snapshot (
    capital_snapshot_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    net_capital REAL NOT NULL,
    tier1_capital REAL,
    total_capital REAL,
    risk_weighted_assets REAL,
    CONSTRAINT ck_capital_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_capital_snapshot_net_capital CHECK (net_capital >= 0),
    CONSTRAINT ck_capital_snapshot_tier1_capital CHECK (tier1_capital >= 0),
    CONSTRAINT ck_capital_snapshot_total_capital CHECK (total_capital >= 0),
    CONSTRAINT ck_capital_snapshot_risk_weighted_assets CHECK (risk_weighted_assets >= 0),
    CONSTRAINT pk_capital_snapshot PRIMARY KEY (capital_snapshot_id),
    CONSTRAINT uq_capital_snapshot_1 UNIQUE (institution_id, as_of_date, currency_code),
    CONSTRAINT fk_capital_snapshot_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE exposure_group (
    exposure_group_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    group_name TEXT NOT NULL,
    group_type TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_exposure_group_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_exposure_group PRIMARY KEY (exposure_group_id),
    CONSTRAINT fk_exposure_group_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE exposure_group_member (
    exposure_member_id TEXT NOT NULL,
    exposure_group_id TEXT NOT NULL,
    party_id TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    CONSTRAINT ck_exposure_group_member_effective_to CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CONSTRAINT pk_exposure_group_member PRIMARY KEY (exposure_member_id),
    CONSTRAINT fk_exposure_group_member_exposure_group_id FOREIGN KEY (exposure_group_id) REFERENCES exposure_group (exposure_group_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_exposure_group_member_party_id FOREIGN KEY (party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE risk_exposure (
    exposure_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    obligor_party_id TEXT,
    exposure_group_id TEXT,
    agreement_id TEXT,
    as_of_date TEXT NOT NULL,
    exposure_type TEXT NOT NULL,
    gross_exposure REAL NOT NULL,
    mitigated_exposure REAL,
    risk_weight REAL,
    currency_code TEXT NOT NULL,
    CONSTRAINT ck_risk_exposure_gross_exposure CHECK (gross_exposure >= 0),
    CONSTRAINT ck_risk_exposure_mitigated_exposure CHECK (mitigated_exposure >= 0),
    CONSTRAINT ck_risk_exposure_risk_weight CHECK (risk_weight >= 0),
    CONSTRAINT ck_risk_exposure_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_risk_exposure PRIMARY KEY (exposure_id),
    CONSTRAINT ck_risk_exposure_table_1 CHECK ((CASE WHEN obligor_party_id IS NULL THEN 0 ELSE 1 END + CASE WHEN exposure_group_id IS NULL THEN 0 ELSE 1 END) >= 1),
    CONSTRAINT fk_risk_exposure_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_exposure_obligor_party_id FOREIGN KEY (obligor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_exposure_exposure_group_id FOREIGN KEY (exposure_group_id) REFERENCES exposure_group (exposure_group_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_exposure_agreement_id FOREIGN KEY (agreement_id) REFERENCES credit_agreement (agreement_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE gl_account (
    gl_account_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    parent_gl_account_id TEXT,
    account_label TEXT NOT NULL,
    account_category TEXT NOT NULL,
    balance_side TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    status TEXT NOT NULL,
    CONSTRAINT ck_gl_account_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_gl_account PRIMARY KEY (gl_account_id),
    CONSTRAINT fk_gl_account_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_gl_account_parent_gl_account_id FOREIGN KEY (parent_gl_account_id) REFERENCES gl_account (gl_account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE gl_balance_snapshot (
    gl_balance_id TEXT NOT NULL,
    gl_account_id TEXT NOT NULL,
    org_unit_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    period_type TEXT NOT NULL,
    debit_balance REAL NOT NULL,
    credit_balance REAL NOT NULL,
    CONSTRAINT ck_gl_balance_snapshot_debit_balance CHECK (debit_balance >= 0),
    CONSTRAINT ck_gl_balance_snapshot_credit_balance CHECK (credit_balance >= 0),
    CONSTRAINT pk_gl_balance_snapshot PRIMARY KEY (gl_balance_id),
    CONSTRAINT uq_gl_balance_snapshot_1 UNIQUE (gl_account_id, org_unit_id, as_of_date, period_type),
    CONSTRAINT fk_gl_balance_snapshot_gl_account_id FOREIGN KEY (gl_account_id) REFERENCES gl_account (gl_account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_gl_balance_snapshot_org_unit_id FOREIGN KEY (org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE liquidity_bucket_snapshot (
    liquidity_bucket_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    bucket_start_days INTEGER NOT NULL,
    bucket_end_days INTEGER,
    currency_code TEXT NOT NULL,
    cash_inflow REAL NOT NULL,
    cash_outflow REAL NOT NULL,
    liquid_assets REAL,
    stable_funding REAL,
    CONSTRAINT ck_liquidity_bucket_snapshot_bucket_start_days CHECK (bucket_start_days >= 0),
    CONSTRAINT ck_liquidity_bucket_snapshot_bucket_end_days CHECK (bucket_end_days IS NULL OR bucket_end_days >= bucket_start_days),
    CONSTRAINT ck_liquidity_bucket_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_liquidity_bucket_snapshot_cash_inflow CHECK (cash_inflow >= 0),
    CONSTRAINT ck_liquidity_bucket_snapshot_cash_outflow CHECK (cash_outflow >= 0),
    CONSTRAINT ck_liquidity_bucket_snapshot_liquid_assets CHECK (liquid_assets >= 0),
    CONSTRAINT ck_liquidity_bucket_snapshot_stable_funding CHECK (stable_funding >= 0),
    CONSTRAINT pk_liquidity_bucket_snapshot PRIMARY KEY (liquidity_bucket_id),
    CONSTRAINT fk_liquidity_bucket_snapshot_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE financial_instrument (
    instrument_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    instrument_type TEXT NOT NULL,
    issuer_party_id TEXT,
    applicant_party_id TEXT,
    beneficiary_party_id TEXT,
    issue_account_id TEXT,
    margin_account_id TEXT,
    face_value REAL NOT NULL,
    margin_amount REAL,
    currency_code TEXT NOT NULL,
    issued_on TEXT NOT NULL,
    maturity_on TEXT,
    trade_background_token TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_financial_instrument_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_financial_instrument_face_value CHECK (face_value >= 0),
    CONSTRAINT ck_financial_instrument_margin_amount CHECK (margin_amount >= 0),
    CONSTRAINT ck_financial_instrument_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_financial_instrument_maturity_on CHECK (maturity_on IS NULL OR maturity_on >= issued_on),
    CONSTRAINT pk_financial_instrument PRIMARY KEY (instrument_id),
    CONSTRAINT fk_financial_instrument_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_financial_instrument_issuer_party_id FOREIGN KEY (issuer_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_financial_instrument_applicant_party_id FOREIGN KEY (applicant_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_financial_instrument_beneficiary_party_id FOREIGN KEY (beneficiary_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_financial_instrument_issue_account_id FOREIGN KEY (issue_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_financial_instrument_margin_account_id FOREIGN KEY (margin_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE market_trade (
    market_trade_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    instrument_id TEXT,
    counterparty_party_id TEXT,
    trade_type TEXT NOT NULL,
    business_date TEXT NOT NULL,
    trade_time TEXT,
    notional_amount REAL NOT NULL,
    settlement_amount REAL,
    currency_code TEXT NOT NULL,
    price REAL,
    interest_rate REAL,
    settlement_account_id TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_market_trade_notional_amount CHECK (notional_amount >= 0),
    CONSTRAINT ck_market_trade_settlement_amount CHECK (settlement_amount >= 0),
    CONSTRAINT ck_market_trade_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_market_trade_price CHECK (price IS NULL OR price >= 0),
    CONSTRAINT ck_market_trade_interest_rate CHECK (interest_rate >= 0),
    CONSTRAINT pk_market_trade PRIMARY KEY (market_trade_id),
    CONSTRAINT fk_market_trade_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_market_trade_instrument_id FOREIGN KEY (instrument_id) REFERENCES financial_instrument (instrument_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_market_trade_counterparty_party_id FOREIGN KEY (counterparty_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_market_trade_settlement_account_id FOREIGN KEY (settlement_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE market_position (
    position_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    instrument_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    quantity REAL,
    carrying_amount REAL NOT NULL,
    fair_value REAL,
    currency_code TEXT NOT NULL,
    CONSTRAINT ck_market_position_quantity CHECK (quantity >= 0),
    CONSTRAINT ck_market_position_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_market_position PRIMARY KEY (position_id),
    CONSTRAINT fk_market_position_institution_id FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_market_position_instrument_id FOREIGN KEY (instrument_id) REFERENCES financial_instrument (instrument_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE fx_rate (
    fx_rate_id TEXT NOT NULL,
    rate_date TEXT NOT NULL,
    base_currency TEXT NOT NULL,
    quote_currency TEXT NOT NULL,
    rate_value REAL NOT NULL,
    rate_type TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    CONSTRAINT ck_fx_rate_base_currency CHECK (length(base_currency) = 3 AND base_currency = upper(base_currency) AND base_currency NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_fx_rate_quote_currency CHECK (length(quote_currency) = 3 AND quote_currency = upper(quote_currency) AND quote_currency NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_fx_rate_rate_value CHECK (rate_value >= 0),
    CONSTRAINT pk_fx_rate PRIMARY KEY (fx_rate_id),
    CONSTRAINT uq_fx_rate_1 UNIQUE (rate_date, base_currency, quote_currency, rate_type),
    CONSTRAINT ck_fx_rate_table_1 CHECK (base_currency <> quote_currency),
    CONSTRAINT ck_fx_rate_table_2 CHECK (rate_value > 0)
) STRICT;

CREATE TABLE reference_rate (
    reference_rate_id TEXT NOT NULL,
    rate_name TEXT NOT NULL,
    tenor_code TEXT,
    effective_date TEXT NOT NULL,
    rate_value REAL NOT NULL,
    currency_code TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    CONSTRAINT ck_reference_rate_rate_value CHECK (rate_value >= 0),
    CONSTRAINT ck_reference_rate_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_reference_rate PRIMARY KEY (reference_rate_id),
    CONSTRAINT uq_reference_rate_1 UNIQUE (rate_name, tenor_code, effective_date, currency_code),
    CONSTRAINT ck_reference_rate_table_1 CHECK (rate_value >= 0)
) STRICT;

CREATE TABLE classification_grade (
    grade_code TEXT NOT NULL,
    grade_name_zh TEXT NOT NULL,
    grade_name_en TEXT NOT NULL,
    grade_ordinal INTEGER NOT NULL UNIQUE,
    is_nonperforming INTEGER NOT NULL,
    CONSTRAINT ck_classification_grade_grade_ordinal CHECK (grade_ordinal > 0),
    CONSTRAINT pk_classification_grade PRIMARY KEY (grade_code)
) STRICT;

CREATE TABLE risk_classification (
    classification_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    grade_code TEXT NOT NULL,
    classification_basis TEXT,
    assessed_org_unit_id TEXT,
    assessed_by_staff_id TEXT,
    CONSTRAINT pk_risk_classification PRIMARY KEY (classification_id),
    CONSTRAINT uq_risk_classification_1 UNIQUE (loan_id, as_of_date),
    CONSTRAINT fk_risk_classification_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_classification_grade_code FOREIGN KEY (grade_code) REFERENCES classification_grade (grade_code) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_classification_assessed_org_unit_id FOREIGN KEY (assessed_org_unit_id) REFERENCES organization_unit (org_unit_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_risk_classification_assessed_by_staff_id FOREIGN KEY (assessed_by_staff_id) REFERENCES staff_member (staff_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE delinquency_snapshot (
    delinquency_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    principal_overdue_days INTEGER NOT NULL,
    interest_overdue_days INTEGER NOT NULL,
    overdue_principal REAL NOT NULL,
    overdue_interest REAL NOT NULL,
    CONSTRAINT ck_delinquency_snapshot_principal_overdue_days CHECK (principal_overdue_days >= 0),
    CONSTRAINT ck_delinquency_snapshot_interest_overdue_days CHECK (interest_overdue_days >= 0),
    CONSTRAINT ck_delinquency_snapshot_overdue_principal CHECK (overdue_principal >= 0),
    CONSTRAINT ck_delinquency_snapshot_overdue_interest CHECK (overdue_interest >= 0),
    CONSTRAINT pk_delinquency_snapshot PRIMARY KEY (delinquency_id),
    CONSTRAINT uq_delinquency_snapshot_1 UNIQUE (loan_id, as_of_date),
    CONSTRAINT fk_delinquency_snapshot_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE provision_snapshot (
    provision_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    provision_stage TEXT,
    required_amount REAL NOT NULL,
    recognized_amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    calculation_method TEXT,
    CONSTRAINT ck_provision_snapshot_required_amount CHECK (required_amount >= 0),
    CONSTRAINT ck_provision_snapshot_recognized_amount CHECK (recognized_amount >= 0),
    CONSTRAINT ck_provision_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_provision_snapshot PRIMARY KEY (provision_id),
    CONSTRAINT uq_provision_snapshot_1 UNIQUE (loan_id, as_of_date),
    CONSTRAINT fk_provision_snapshot_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE asset_resolution_event (
    resolution_id TEXT NOT NULL,
    loan_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    amount REAL NOT NULL,
    currency_code TEXT NOT NULL,
    counterparty_party_id TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_asset_resolution_event_amount CHECK (amount >= 0),
    CONSTRAINT ck_asset_resolution_event_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT pk_asset_resolution_event PRIMARY KEY (resolution_id),
    CONSTRAINT fk_asset_resolution_event_loan_id FOREIGN KEY (loan_id) REFERENCES loan_drawdown (loan_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_asset_resolution_event_counterparty_party_id FOREIGN KEY (counterparty_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE wealth_product (
    product_id TEXT NOT NULL,
    issuer_institution_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    offering_type TEXT NOT NULL,
    operation_mode TEXT NOT NULL,
    investment_nature TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    target_investor_type TEXT,
    currency_code TEXT NOT NULL,
    planned_raise_amount REAL,
    actual_raise_amount REAL,
    offering_start_on TEXT,
    offering_end_on TEXT,
    inception_on TEXT NOT NULL,
    scheduled_maturity_on TEXT,
    actual_termination_on TEXT,
    minimum_holding_days INTEGER,
    customer_redemption_allowed INTEGER NOT NULL,
    is_cash_management INTEGER NOT NULL,
    is_structured INTEGER NOT NULL,
    benchmark_floor_rate REAL,
    benchmark_ceiling_rate REAL,
    management_fee_rate REAL,
    custody_fee_rate REAL,
    manager_party_id TEXT,
    custodian_party_id TEXT,
    status TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_wealth_product_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT ck_wealth_product_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_wealth_product_planned_raise_amount CHECK (planned_raise_amount >= 0),
    CONSTRAINT ck_wealth_product_actual_raise_amount CHECK (actual_raise_amount >= 0),
    CONSTRAINT ck_wealth_product_offering_end_on CHECK (offering_end_on IS NULL OR offering_start_on IS NULL OR offering_end_on >= offering_start_on),
    CONSTRAINT ck_wealth_product_scheduled_maturity_on CHECK (scheduled_maturity_on IS NULL OR scheduled_maturity_on >= inception_on),
    CONSTRAINT ck_wealth_product_actual_termination_on CHECK (actual_termination_on IS NULL OR actual_termination_on >= inception_on),
    CONSTRAINT ck_wealth_product_minimum_holding_days CHECK (minimum_holding_days IS NULL OR minimum_holding_days >= 0),
    CONSTRAINT ck_wealth_product_benchmark_floor_rate CHECK (benchmark_floor_rate >= 0),
    CONSTRAINT ck_wealth_product_benchmark_ceiling_rate CHECK (benchmark_ceiling_rate >= 0),
    CONSTRAINT ck_wealth_product_management_fee_rate CHECK (management_fee_rate >= 0),
    CONSTRAINT ck_wealth_product_custody_fee_rate CHECK (custody_fee_rate >= 0),
    CONSTRAINT pk_wealth_product PRIMARY KEY (product_id),
    CONSTRAINT ck_wealth_product_table_1 CHECK (benchmark_ceiling_rate IS NULL OR benchmark_floor_rate IS NULL OR benchmark_ceiling_rate >= benchmark_floor_rate),
    CONSTRAINT fk_wealth_product_issuer_institution_id FOREIGN KEY (issuer_institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_wealth_product_manager_party_id FOREIGN KEY (manager_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_wealth_product_custodian_party_id FOREIGN KEY (custodian_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE wealth_product_snapshot (
    product_snapshot_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    outstanding_balance REAL NOT NULL,
    outstanding_units REAL,
    unit_net_value REAL,
    cumulative_net_value REAL,
    total_asset_amount REAL,
    total_liability_amount REAL,
    reported_leverage_ratio REAL,
    cumulative_subscription_amount REAL,
    cumulative_redemption_amount REAL,
    realized_yield REAL,
    CONSTRAINT ck_wealth_product_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_wealth_product_snapshot_outstanding_balance CHECK (outstanding_balance >= 0),
    CONSTRAINT ck_wealth_product_snapshot_outstanding_units CHECK (outstanding_units IS NULL OR outstanding_units >= 0),
    CONSTRAINT ck_wealth_product_snapshot_unit_net_value CHECK (unit_net_value IS NULL OR unit_net_value >= 0),
    CONSTRAINT ck_wealth_product_snapshot_cumulative_net_value CHECK (cumulative_net_value IS NULL OR cumulative_net_value >= 0),
    CONSTRAINT ck_wealth_product_snapshot_total_asset_amount CHECK (total_asset_amount >= 0),
    CONSTRAINT ck_wealth_product_snapshot_total_liability_amount CHECK (total_liability_amount >= 0),
    CONSTRAINT ck_wealth_product_snapshot_reported_leverage_ratio CHECK (reported_leverage_ratio >= 0),
    CONSTRAINT ck_wealth_product_snapshot_cumulative_subscription_amount CHECK (cumulative_subscription_amount >= 0),
    CONSTRAINT ck_wealth_product_snapshot_cumulative_redemption_amount CHECK (cumulative_redemption_amount >= 0),
    CONSTRAINT ck_wealth_product_snapshot_realized_yield CHECK (realized_yield >= 0),
    CONSTRAINT pk_wealth_product_snapshot PRIMARY KEY (product_snapshot_id),
    CONSTRAINT uq_wealth_product_snapshot_1 UNIQUE (product_id, as_of_date),
    CONSTRAINT fk_wealth_product_snapshot_product_id FOREIGN KEY (product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE managed_asset (
    asset_id TEXT NOT NULL,
    originator_institution_id TEXT NOT NULL,
    asset_name TEXT NOT NULL,
    asset_scope TEXT NOT NULL,
    asset_category_primary TEXT NOT NULL,
    asset_category_secondary TEXT,
    issuer_party_id TEXT,
    obligor_party_id TEXT,
    industry_code TEXT,
    country_code TEXT,
    market_venue TEXT,
    currency_code TEXT NOT NULL,
    issued_amount REAL,
    interest_start_on TEXT,
    maturity_on TEXT,
    annual_yield_rate REAL,
    internal_rating TEXT,
    external_rating TEXT,
    valuation_method TEXT,
    observed_on TEXT,
    is_liability INTEGER NOT NULL,
    status TEXT NOT NULL,
    CONSTRAINT ck_managed_asset_country_code CHECK (country_code IS NULL OR length(country_code) = 2 AND country_code = upper(country_code) AND country_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_managed_asset_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_managed_asset_issued_amount CHECK (issued_amount >= 0),
    CONSTRAINT ck_managed_asset_maturity_on CHECK (maturity_on IS NULL OR interest_start_on IS NULL OR maturity_on >= interest_start_on),
    CONSTRAINT ck_managed_asset_annual_yield_rate CHECK (annual_yield_rate >= 0),
    CONSTRAINT pk_managed_asset PRIMARY KEY (asset_id),
    CONSTRAINT fk_managed_asset_originator_institution_id FOREIGN KEY (originator_institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_managed_asset_issuer_party_id FOREIGN KEY (issuer_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_managed_asset_obligor_party_id FOREIGN KEY (obligor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_managed_asset_industry_code FOREIGN KEY (industry_code) REFERENCES industry_sector (sector_code) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE private_credit_profile (
    asset_id TEXT NOT NULL,
    project_name TEXT,
    project_industry_code TEXT,
    is_monitored_sector INTEGER NOT NULL,
    financing_party_size TEXT,
    financing_party_economic_type TEXT,
    project_return_rate REAL,
    interest_payment_interval_months INTEGER,
    repayment_type TEXT,
    guarantee_type TEXT,
    collateral_type TEXT,
    collateral_value REAL,
    option_type TEXT,
    perpetual_term_type TEXT,
    first_reset_on TEXT,
    reset_interval_months INTEGER,
    CONSTRAINT ck_private_credit_profile_project_return_rate CHECK (project_return_rate >= 0),
    CONSTRAINT ck_private_credit_profile_interest_payment_interval_months CHECK (interest_payment_interval_months IS NULL OR interest_payment_interval_months > 0),
    CONSTRAINT ck_private_credit_profile_collateral_value CHECK (collateral_value >= 0),
    CONSTRAINT ck_private_credit_profile_reset_interval_months CHECK (reset_interval_months IS NULL OR reset_interval_months > 0),
    CONSTRAINT pk_private_credit_profile PRIMARY KEY (asset_id),
    CONSTRAINT fk_private_credit_profile_asset_id FOREIGN KEY (asset_id) REFERENCES managed_asset (asset_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_private_credit_profile_project_industry_code FOREIGN KEY (project_industry_code) REFERENCES industry_sector (sector_code) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE product_holding_snapshot (
    holding_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    investment_path TEXT NOT NULL,
    lookthrough_depth INTEGER NOT NULL,
    intermediary_party_id TEXT,
    currency_code TEXT NOT NULL,
    quantity REAL,
    carrying_amount REAL NOT NULL,
    fair_value REAL,
    converted_amount REAL,
    clean_valuation_price REAL,
    full_valuation_price REAL,
    remaining_term_days INTEGER,
    CONSTRAINT ck_product_holding_snapshot_lookthrough_depth CHECK (lookthrough_depth >= 0),
    CONSTRAINT ck_product_holding_snapshot_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_product_holding_snapshot_quantity CHECK (quantity IS NULL OR quantity >= 0),
    CONSTRAINT ck_product_holding_snapshot_carrying_amount CHECK (carrying_amount >= 0),
    CONSTRAINT ck_product_holding_snapshot_fair_value CHECK (fair_value >= 0),
    CONSTRAINT ck_product_holding_snapshot_converted_amount CHECK (converted_amount >= 0),
    CONSTRAINT ck_product_holding_snapshot_clean_valuation_price CHECK (clean_valuation_price IS NULL OR clean_valuation_price >= 0),
    CONSTRAINT ck_product_holding_snapshot_full_valuation_price CHECK (full_valuation_price IS NULL OR full_valuation_price >= 0),
    CONSTRAINT ck_product_holding_snapshot_remaining_term_days CHECK (remaining_term_days IS NULL OR remaining_term_days >= 0),
    CONSTRAINT pk_product_holding_snapshot PRIMARY KEY (holding_id),
    CONSTRAINT uq_product_holding_snapshot_1 UNIQUE (product_id, asset_id, as_of_date, investment_path),
    CONSTRAINT fk_product_holding_snapshot_product_id FOREIGN KEY (product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_holding_snapshot_asset_id FOREIGN KEY (asset_id) REFERENCES managed_asset (asset_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_holding_snapshot_intermediary_party_id FOREIGN KEY (intermediary_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE product_asset_trade (
    asset_trade_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    counterparty_party_id TEXT,
    counterparty_product_id TEXT,
    trade_type TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    initiated_at TEXT,
    currency_code TEXT NOT NULL,
    trade_amount REAL NOT NULL,
    converted_amount REAL,
    quantity REAL,
    clean_price REAL,
    full_price REAL,
    yield_to_maturity REAL,
    market_venue TEXT,
    valuation_method TEXT,
    status TEXT NOT NULL,
    CONSTRAINT ck_product_asset_trade_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_product_asset_trade_trade_amount CHECK (trade_amount >= 0),
    CONSTRAINT ck_product_asset_trade_converted_amount CHECK (converted_amount >= 0),
    CONSTRAINT ck_product_asset_trade_quantity CHECK (quantity IS NULL OR quantity >= 0),
    CONSTRAINT ck_product_asset_trade_clean_price CHECK (clean_price IS NULL OR clean_price >= 0),
    CONSTRAINT ck_product_asset_trade_full_price CHECK (full_price IS NULL OR full_price >= 0),
    CONSTRAINT ck_product_asset_trade_yield_to_maturity CHECK (yield_to_maturity >= 0),
    CONSTRAINT pk_product_asset_trade PRIMARY KEY (asset_trade_id),
    CONSTRAINT ck_product_asset_trade_table_1 CHECK ((CASE WHEN counterparty_party_id IS NULL THEN 0 ELSE 1 END + CASE WHEN counterparty_product_id IS NULL THEN 0 ELSE 1 END) <= 1),
    CONSTRAINT ck_product_asset_trade_table_2 CHECK (counterparty_product_id IS NULL OR counterparty_product_id <> product_id),
    CONSTRAINT fk_product_asset_trade_product_id FOREIGN KEY (product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_asset_trade_asset_id FOREIGN KEY (asset_id) REFERENCES managed_asset (asset_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_asset_trade_counterparty_party_id FOREIGN KEY (counterparty_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_asset_trade_counterparty_product_id FOREIGN KEY (counterparty_product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE product_sale_event (
    sale_event_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    investor_party_id TEXT NOT NULL,
    funding_account_id TEXT,
    distributor_party_id TEXT,
    operator_id TEXT,
    sale_type TEXT NOT NULL,
    business_date TEXT NOT NULL,
    confirmed_at TEXT,
    currency_code TEXT NOT NULL,
    confirmed_nav REAL,
    confirmed_amount REAL NOT NULL,
    converted_amount REAL,
    confirmed_units REAL,
    fee_amount REAL,
    channel TEXT,
    is_agency_sale INTEGER NOT NULL,
    status TEXT NOT NULL,
    CONSTRAINT ck_product_sale_event_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_product_sale_event_confirmed_nav CHECK (confirmed_nav IS NULL OR confirmed_nav >= 0),
    CONSTRAINT ck_product_sale_event_confirmed_amount CHECK (confirmed_amount >= 0),
    CONSTRAINT ck_product_sale_event_converted_amount CHECK (converted_amount >= 0),
    CONSTRAINT ck_product_sale_event_confirmed_units CHECK (confirmed_units IS NULL OR confirmed_units >= 0),
    CONSTRAINT ck_product_sale_event_fee_amount CHECK (fee_amount >= 0),
    CONSTRAINT pk_product_sale_event PRIMARY KEY (sale_event_id),
    CONSTRAINT ck_product_sale_event_table_1 CHECK (NOT is_agency_sale OR distributor_party_id IS NOT NULL),
    CONSTRAINT fk_product_sale_event_product_id FOREIGN KEY (product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_sale_event_investor_party_id FOREIGN KEY (investor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_sale_event_funding_account_id FOREIGN KEY (funding_account_id) REFERENCES account (account_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_sale_event_distributor_party_id FOREIGN KEY (distributor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_product_sale_event_operator_id FOREIGN KEY (operator_id) REFERENCES service_operator (operator_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE TABLE investor_product_position (
    investor_position_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    investor_party_id TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    currency_code TEXT NOT NULL,
    units REAL NOT NULL,
    position_balance REAL NOT NULL,
    converted_balance REAL,
    cost_basis REAL,
    status TEXT NOT NULL,
    CONSTRAINT ck_investor_product_position_currency_code CHECK (length(currency_code) = 3 AND currency_code = upper(currency_code) AND currency_code NOT GLOB '*[^A-Z]*'),
    CONSTRAINT ck_investor_product_position_units CHECK (units >= 0),
    CONSTRAINT ck_investor_product_position_position_balance CHECK (position_balance >= 0),
    CONSTRAINT ck_investor_product_position_converted_balance CHECK (converted_balance >= 0),
    CONSTRAINT ck_investor_product_position_cost_basis CHECK (cost_basis >= 0),
    CONSTRAINT pk_investor_product_position PRIMARY KEY (investor_position_id),
    CONSTRAINT uq_investor_product_position_1 UNIQUE (product_id, investor_party_id, as_of_date),
    CONSTRAINT fk_investor_product_position_product_id FOREIGN KEY (product_id) REFERENCES wealth_product (product_id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_investor_product_position_investor_party_id FOREIGN KEY (investor_party_id) REFERENCES party (party_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE INDEX ix_organization_unit_effective_from ON organization_unit (effective_from);
CREATE INDEX ix_organization_unit_institution_id ON organization_unit (institution_id);
CREATE INDEX ix_organization_unit_parent_org_unit_id ON organization_unit (parent_org_unit_id);
CREATE INDEX ix_staff_member_home_org_unit_id ON staff_member (home_org_unit_id);
CREATE INDEX ix_staff_member_person_party_id ON staff_member (person_party_id);
CREATE INDEX ix_staff_assignment_effective_from ON staff_assignment (effective_from);
CREATE INDEX ix_staff_assignment_org_unit_id ON staff_assignment (org_unit_id);
CREATE INDEX ix_staff_assignment_staff_id ON staff_assignment (staff_id);
CREATE INDEX ix_service_operator_org_unit_id ON service_operator (org_unit_id);
CREATE INDEX ix_service_operator_staff_id ON service_operator (staff_id);
CREATE INDEX ix_party_home_org_unit_id ON party (home_org_unit_id);
CREATE INDEX ix_person_profile_employer_party_id ON person_profile (employer_party_id);
CREATE INDEX ix_person_profile_party_id ON person_profile (party_id);
CREATE INDEX ix_industry_sector_parent_sector_code ON industry_sector (parent_sector_code);
CREATE INDEX ix_organization_profile_industry_code ON organization_profile (industry_code);
CREATE INDEX ix_organization_profile_legal_representative_party_id ON organization_profile (legal_representative_party_id);
CREATE INDEX ix_organization_profile_party_id ON organization_profile (party_id);
CREATE INDEX ix_party_relation_effective_from ON party_relation (effective_from);
CREATE INDEX ix_party_relation_source_party_id ON party_relation (source_party_id);
CREATE INDEX ix_party_relation_target_party_id ON party_relation (target_party_id);
CREATE INDEX ix_ownership_interest_effective_from ON ownership_interest (effective_from);
CREATE INDEX ix_ownership_interest_owner_party_id ON ownership_interest (owner_party_id);
CREATE INDEX ix_ownership_interest_target_party_id ON ownership_interest (target_party_id);
CREATE INDEX ix_group_membership_effective_from ON group_membership (effective_from);
CREATE INDEX ix_group_membership_group_party_id ON group_membership (group_party_id);
CREATE INDEX ix_group_membership_member_party_id ON group_membership (member_party_id);
CREATE INDEX ix_financial_snapshot_as_of_date ON financial_snapshot (as_of_date);
CREATE INDEX ix_financial_snapshot_party_id ON financial_snapshot (party_id);
CREATE INDEX ix_account_institution_id ON account (institution_id);
CREATE INDEX ix_account_org_unit_id ON account (org_unit_id);
CREATE INDEX ix_account_holder_account_id ON account_holder (account_id);
CREATE INDEX ix_account_holder_effective_from ON account_holder (effective_from);
CREATE INDEX ix_account_holder_party_id ON account_holder (party_id);
CREATE INDEX ix_account_balance_snapshot_account_id ON account_balance_snapshot (account_id);
CREATE INDEX ix_account_balance_snapshot_as_of_date ON account_balance_snapshot (as_of_date);
CREATE INDEX ix_payment_event_business_date ON payment_event (business_date);
CREATE INDEX ix_payment_event_event_time ON payment_event (event_time);
CREATE INDEX ix_payment_event_from_account_id ON payment_event (from_account_id);
CREATE INDEX ix_payment_event_operator_id ON payment_event (operator_id);
CREATE INDEX ix_payment_event_origin_org_unit_id ON payment_event (origin_org_unit_id);
CREATE INDEX ix_payment_event_to_account_id ON payment_event (to_account_id);
CREATE INDEX ix_term_deposit_account_id ON term_deposit (account_id);
CREATE INDEX ix_payment_card_holder_party_id ON payment_card (holder_party_id);
CREATE INDEX ix_payment_card_settlement_account_id ON payment_card (settlement_account_id);
CREATE INDEX ix_credit_facility_effective_from ON credit_facility (effective_from);
CREATE INDEX ix_credit_facility_institution_id ON credit_facility (institution_id);
CREATE INDEX ix_credit_facility_obligor_party_id ON credit_facility (obligor_party_id);
CREATE INDEX ix_credit_agreement_borrower_party_id ON credit_agreement (borrower_party_id);
CREATE INDEX ix_credit_agreement_effective_from ON credit_agreement (effective_from);
CREATE INDEX ix_credit_agreement_facility_id ON credit_agreement (facility_id);
CREATE INDEX ix_credit_agreement_institution_id ON credit_agreement (institution_id);
CREATE INDEX ix_credit_agreement_managing_org_unit_id ON credit_agreement (managing_org_unit_id);
CREATE INDEX ix_credit_agreement_target_industry_code ON credit_agreement (target_industry_code);
CREATE INDEX ix_credit_participant_agreement_id ON credit_participant (agreement_id);
CREATE INDEX ix_credit_participant_effective_from ON credit_participant (effective_from);
CREATE INDEX ix_credit_participant_party_id ON credit_participant (party_id);
CREATE INDEX ix_loan_drawdown_agreement_id ON loan_drawdown (agreement_id);
CREATE INDEX ix_loan_drawdown_disbursement_account_id ON loan_drawdown (disbursement_account_id);
CREATE INDEX ix_loan_drawdown_loan_account_id ON loan_drawdown (loan_account_id);
CREATE INDEX ix_loan_drawdown_repayment_account_id ON loan_drawdown (repayment_account_id);
CREATE INDEX ix_loan_balance_snapshot_as_of_date ON loan_balance_snapshot (as_of_date);
CREATE INDEX ix_loan_balance_snapshot_loan_id ON loan_balance_snapshot (loan_id);
CREATE INDEX ix_loan_cashflow_business_date ON loan_cashflow (business_date);
CREATE INDEX ix_loan_cashflow_loan_id ON loan_cashflow (loan_id);
CREATE INDEX ix_loan_cashflow_payment_id ON loan_cashflow (payment_id);
CREATE INDEX ix_repayment_schedule_loan_id ON repayment_schedule (loan_id);
CREATE INDEX ix_payment_instruction_intended_payee_account_id ON payment_instruction (intended_payee_account_id);
CREATE INDEX ix_payment_instruction_intended_payee_party_id ON payment_instruction (intended_payee_party_id);
CREATE INDEX ix_payment_instruction_loan_id ON payment_instruction (loan_id);
CREATE INDEX ix_loan_lineage_predecessor_loan_id ON loan_lineage (predecessor_loan_id);
CREATE INDEX ix_loan_lineage_successor_loan_id ON loan_lineage (successor_loan_id);
CREATE INDEX ix_security_agreement_effective_from ON security_agreement (effective_from);
CREATE INDEX ix_security_agreement_institution_id ON security_agreement (institution_id);
CREATE INDEX ix_security_agreement_manager_staff_id ON security_agreement (manager_staff_id);
CREATE INDEX ix_secured_obligation_agreement_id ON secured_obligation (agreement_id);
CREATE INDEX ix_secured_obligation_effective_from ON secured_obligation (effective_from);
CREATE INDEX ix_secured_obligation_instrument_id ON secured_obligation (instrument_id);
CREATE INDEX ix_secured_obligation_security_id ON secured_obligation (security_id);
CREATE INDEX ix_guarantor_commitment_effective_from ON guarantor_commitment (effective_from);
CREATE INDEX ix_guarantor_commitment_guarantor_party_id ON guarantor_commitment (guarantor_party_id);
CREATE INDEX ix_guarantor_commitment_security_id ON guarantor_commitment (security_id);
CREATE INDEX ix_collateral_asset_owner_party_id ON collateral_asset (owner_party_id);
CREATE INDEX ix_collateral_link_collateral_id ON collateral_link (collateral_id);
CREATE INDEX ix_collateral_link_effective_from ON collateral_link (effective_from);
CREATE INDEX ix_collateral_link_security_id ON collateral_link (security_id);
CREATE INDEX ix_collateral_valuation_collateral_id ON collateral_valuation (collateral_id);
CREATE INDEX ix_capital_snapshot_as_of_date ON capital_snapshot (as_of_date);
CREATE INDEX ix_capital_snapshot_institution_id ON capital_snapshot (institution_id);
CREATE INDEX ix_exposure_group_effective_from ON exposure_group (effective_from);
CREATE INDEX ix_exposure_group_institution_id ON exposure_group (institution_id);
CREATE INDEX ix_exposure_group_member_effective_from ON exposure_group_member (effective_from);
CREATE INDEX ix_exposure_group_member_exposure_group_id ON exposure_group_member (exposure_group_id);
CREATE INDEX ix_exposure_group_member_party_id ON exposure_group_member (party_id);
CREATE INDEX ix_risk_exposure_agreement_id ON risk_exposure (agreement_id);
CREATE INDEX ix_risk_exposure_as_of_date ON risk_exposure (as_of_date);
CREATE INDEX ix_risk_exposure_exposure_group_id ON risk_exposure (exposure_group_id);
CREATE INDEX ix_risk_exposure_institution_id ON risk_exposure (institution_id);
CREATE INDEX ix_risk_exposure_obligor_party_id ON risk_exposure (obligor_party_id);
CREATE INDEX ix_gl_account_institution_id ON gl_account (institution_id);
CREATE INDEX ix_gl_account_parent_gl_account_id ON gl_account (parent_gl_account_id);
CREATE INDEX ix_gl_balance_snapshot_as_of_date ON gl_balance_snapshot (as_of_date);
CREATE INDEX ix_gl_balance_snapshot_gl_account_id ON gl_balance_snapshot (gl_account_id);
CREATE INDEX ix_gl_balance_snapshot_org_unit_id ON gl_balance_snapshot (org_unit_id);
CREATE INDEX ix_liquidity_bucket_snapshot_as_of_date ON liquidity_bucket_snapshot (as_of_date);
CREATE INDEX ix_liquidity_bucket_snapshot_institution_id ON liquidity_bucket_snapshot (institution_id);
CREATE INDEX ix_financial_instrument_applicant_party_id ON financial_instrument (applicant_party_id);
CREATE INDEX ix_financial_instrument_beneficiary_party_id ON financial_instrument (beneficiary_party_id);
CREATE INDEX ix_financial_instrument_institution_id ON financial_instrument (institution_id);
CREATE INDEX ix_financial_instrument_issue_account_id ON financial_instrument (issue_account_id);
CREATE INDEX ix_financial_instrument_issuer_party_id ON financial_instrument (issuer_party_id);
CREATE INDEX ix_financial_instrument_margin_account_id ON financial_instrument (margin_account_id);
CREATE INDEX ix_market_trade_business_date ON market_trade (business_date);
CREATE INDEX ix_market_trade_counterparty_party_id ON market_trade (counterparty_party_id);
CREATE INDEX ix_market_trade_institution_id ON market_trade (institution_id);
CREATE INDEX ix_market_trade_instrument_id ON market_trade (instrument_id);
CREATE INDEX ix_market_trade_settlement_account_id ON market_trade (settlement_account_id);
CREATE INDEX ix_market_position_as_of_date ON market_position (as_of_date);
CREATE INDEX ix_market_position_institution_id ON market_position (institution_id);
CREATE INDEX ix_market_position_instrument_id ON market_position (instrument_id);
CREATE INDEX ix_risk_classification_as_of_date ON risk_classification (as_of_date);
CREATE INDEX ix_risk_classification_assessed_by_staff_id ON risk_classification (assessed_by_staff_id);
CREATE INDEX ix_risk_classification_assessed_org_unit_id ON risk_classification (assessed_org_unit_id);
CREATE INDEX ix_risk_classification_grade_code ON risk_classification (grade_code);
CREATE INDEX ix_risk_classification_loan_id ON risk_classification (loan_id);
CREATE INDEX ix_delinquency_snapshot_as_of_date ON delinquency_snapshot (as_of_date);
CREATE INDEX ix_delinquency_snapshot_loan_id ON delinquency_snapshot (loan_id);
CREATE INDEX ix_provision_snapshot_as_of_date ON provision_snapshot (as_of_date);
CREATE INDEX ix_provision_snapshot_loan_id ON provision_snapshot (loan_id);
CREATE INDEX ix_asset_resolution_event_counterparty_party_id ON asset_resolution_event (counterparty_party_id);
CREATE INDEX ix_asset_resolution_event_loan_id ON asset_resolution_event (loan_id);
CREATE INDEX ix_wealth_product_custodian_party_id ON wealth_product (custodian_party_id);
CREATE INDEX ix_wealth_product_issuer_institution_id ON wealth_product (issuer_institution_id);
CREATE INDEX ix_wealth_product_manager_party_id ON wealth_product (manager_party_id);
CREATE INDEX ix_wealth_product_snapshot_as_of_date ON wealth_product_snapshot (as_of_date);
CREATE INDEX ix_wealth_product_snapshot_product_id ON wealth_product_snapshot (product_id);
CREATE INDEX ix_managed_asset_industry_code ON managed_asset (industry_code);
CREATE INDEX ix_managed_asset_issuer_party_id ON managed_asset (issuer_party_id);
CREATE INDEX ix_managed_asset_obligor_party_id ON managed_asset (obligor_party_id);
CREATE INDEX ix_managed_asset_originator_institution_id ON managed_asset (originator_institution_id);
CREATE INDEX ix_private_credit_profile_asset_id ON private_credit_profile (asset_id);
CREATE INDEX ix_private_credit_profile_project_industry_code ON private_credit_profile (project_industry_code);
CREATE INDEX ix_product_holding_snapshot_as_of_date ON product_holding_snapshot (as_of_date);
CREATE INDEX ix_product_holding_snapshot_asset_id ON product_holding_snapshot (asset_id);
CREATE INDEX ix_product_holding_snapshot_intermediary_party_id ON product_holding_snapshot (intermediary_party_id);
CREATE INDEX ix_product_holding_snapshot_product_id ON product_holding_snapshot (product_id);
CREATE INDEX ix_product_asset_trade_asset_id ON product_asset_trade (asset_id);
CREATE INDEX ix_product_asset_trade_counterparty_party_id ON product_asset_trade (counterparty_party_id);
CREATE INDEX ix_product_asset_trade_counterparty_product_id ON product_asset_trade (counterparty_product_id);
CREATE INDEX ix_product_asset_trade_product_id ON product_asset_trade (product_id);
CREATE INDEX ix_product_sale_event_business_date ON product_sale_event (business_date);
CREATE INDEX ix_product_sale_event_distributor_party_id ON product_sale_event (distributor_party_id);
CREATE INDEX ix_product_sale_event_funding_account_id ON product_sale_event (funding_account_id);
CREATE INDEX ix_product_sale_event_investor_party_id ON product_sale_event (investor_party_id);
CREATE INDEX ix_product_sale_event_operator_id ON product_sale_event (operator_id);
CREATE INDEX ix_product_sale_event_product_id ON product_sale_event (product_id);
CREATE INDEX ix_investor_product_position_as_of_date ON investor_product_position (as_of_date);
CREATE INDEX ix_investor_product_position_investor_party_id ON investor_product_position (investor_party_id);
CREATE INDEX ix_investor_product_position_product_id ON investor_product_position (product_id);

-- Canonical five-category loan classification.  The code for 正常 is NORMAL.
-- (The legacy release shipped PASS here while every gold query filtered on
-- 'NORMAL', which caused 81 foreign-key violations across 25 tasks.)


-- BankRegSQL V3 append-only regulatory evidence extensions.
CREATE TABLE prudential_metric_snapshot_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_prudential_metric_snapshot_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_prudential_metric_snapshot_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_prudential_metric_snapshot_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_prudential_metric_snapshot_v3_event ON prudential_metric_snapshot_v3 (event_code, institution_id, event_date);

CREATE TABLE regulatory_submission_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_regulatory_submission_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_regulatory_submission_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_regulatory_submission_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_regulatory_submission_event_v3_event ON regulatory_submission_event_v3 (event_code, institution_id, event_date);

CREATE TABLE governance_control_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_governance_control_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_governance_control_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_governance_control_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_governance_control_record_v3_event ON governance_control_record_v3 (event_code, institution_id, event_date);

CREATE TABLE customer_due_diligence_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_customer_due_diligence_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_customer_due_diligence_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_customer_due_diligence_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_customer_due_diligence_event_v3_event ON customer_due_diligence_event_v3 (event_code, institution_id, event_date);

CREATE TABLE beneficial_owner_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_beneficial_owner_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_beneficial_owner_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_beneficial_owner_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_beneficial_owner_record_v3_event ON beneficial_owner_record_v3 (event_code, institution_id, event_date);

CREATE TABLE data_security_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_data_security_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_data_security_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_data_security_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_data_security_event_v3_event ON data_security_event_v3 (event_code, institution_id, event_date);

CREATE TABLE ai_system_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_ai_system_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_ai_system_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_ai_system_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_ai_system_record_v3_event ON ai_system_record_v3 (event_code, institution_id, event_date);

CREATE TABLE product_conduct_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_product_conduct_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_product_conduct_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_product_conduct_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_product_conduct_event_v3_event ON product_conduct_event_v3 (event_code, institution_id, event_date);

CREATE TABLE custody_operation_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_custody_operation_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_custody_operation_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_custody_operation_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_custody_operation_event_v3_event ON custody_operation_event_v3 (event_code, institution_id, event_date);

CREATE TABLE fx_business_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_fx_business_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_fx_business_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_fx_business_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_fx_business_event_v3_event ON fx_business_event_v3 (event_code, institution_id, event_date);

CREATE TABLE related_transaction_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_related_transaction_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_related_transaction_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_related_transaction_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_related_transaction_record_v3_event ON related_transaction_record_v3 (event_code, institution_id, event_date);

CREATE TABLE lending_control_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_lending_control_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_lending_control_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_lending_control_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_lending_control_event_v3_event ON lending_control_event_v3 (event_code, institution_id, event_date);

CREATE TABLE deposit_protection_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_deposit_protection_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_deposit_protection_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_deposit_protection_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_deposit_protection_record_v3_event ON deposit_protection_record_v3 (event_code, institution_id, event_date);

CREATE TABLE license_record_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_license_record_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_license_record_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_license_record_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_license_record_v3_event ON license_record_v3 (event_code, institution_id, event_date);

CREATE TABLE operational_risk_event_v3 (
    record_id TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    event_code TEXT NOT NULL,
    event_date TEXT NOT NULL,
    deadline_date TEXT,
    completion_date TEXT,
    observed_value REAL,
    count_value INTEGER,
    amount_value REAL,
    ratio_value REAL,
    status_code TEXT NOT NULL,
    exception_flag INTEGER NOT NULL DEFAULT 0,
    source_record_id TEXT NOT NULL,
    CONSTRAINT pk_operational_risk_event_v3 PRIMARY KEY (record_id),
    CONSTRAINT ck_operational_risk_event_v3_exception CHECK (exception_flag IN (0, 1)),
    CONSTRAINT fk_operational_risk_event_v3_institution FOREIGN KEY (institution_id) REFERENCES institution (institution_id) DEFERRABLE INITIALLY DEFERRED
) STRICT;
CREATE INDEX ix_operational_risk_event_v3_event ON operational_risk_event_v3 (event_code, institution_id, event_date);

-- =============================================================================
-- Controlled-vocabulary layer (BankRegBench-v2)
-- Every opaque code a question may refer to is named here, so a natural-language
-- question can be resolved without the prompt leaking the answer.  The original
-- BankRegSQL warehouse shipped code columns with no such layer, which made its
-- benchmarks either answer-leaking or unanswerable.
-- =============================================================================
CREATE TABLE party_type_catalog (
    party_type TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_party_type_catalog PRIMARY KEY (party_type)
) STRICT;

CREATE TABLE status_catalog (
    entity TEXT NOT NULL, status_code TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_status_catalog PRIMARY KEY (entity, status_code)
) STRICT;

CREATE TABLE loan_product_catalog (
    product_code TEXT NOT NULL, product_name_zh TEXT NOT NULL,
    product_family TEXT NOT NULL, is_working_capital INTEGER NOT NULL,
    CONSTRAINT pk_loan_product_catalog PRIMARY KEY (product_code),
    CONSTRAINT ck_loan_product_wc CHECK (is_working_capital IN (0,1))
) STRICT;

CREATE TABLE payment_mode_catalog (
    payment_mode TEXT NOT NULL, payment_mode_name_zh TEXT NOT NULL,
    CONSTRAINT pk_payment_mode_catalog PRIMARY KEY (payment_mode)
) STRICT;

CREATE TABLE relation_type_catalog (
    relation_type TEXT NOT NULL, relation_name_zh TEXT NOT NULL,
    CONSTRAINT pk_relation_type_catalog PRIMARY KEY (relation_type)
) STRICT;

CREATE TABLE regulatory_event_catalog (
    event_code TEXT NOT NULL, event_name_zh TEXT NOT NULL, rule_family TEXT NOT NULL,
    CONSTRAINT pk_regulatory_event_catalog PRIMARY KEY (event_code)
) STRICT;

CREATE TABLE instrument_type_catalog (
    instrument_type TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_instrument_type_catalog PRIMARY KEY (instrument_type)
) STRICT;

CREATE TABLE card_type_catalog (
    card_type TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_card_type_catalog PRIMARY KEY (card_type)
) STRICT;

CREATE TABLE payment_type_catalog (
    payment_type TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_payment_type_catalog PRIMARY KEY (payment_type)
) STRICT;

CREATE TABLE exposure_group_type_catalog (
    group_type TEXT NOT NULL, name_zh TEXT NOT NULL,
    CONSTRAINT pk_exposure_group_type_catalog PRIMARY KEY (group_type)
) STRICT;
